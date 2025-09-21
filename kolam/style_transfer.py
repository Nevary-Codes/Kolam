import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from flask import Flask, request, jsonify, send_file
import io

# ------------------ Device ------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ------------------ Image Loader ------------------
def load_image(source, size=512):
    if isinstance(source, str):
        if source.startswith("http"):  # URL
            response = requests.get(source)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:  # local path
            image = Image.open(source).convert("RGB")
    elif isinstance(source, Image.Image):
        image = source.convert("RGB")
    else:
        raise ValueError("Unsupported image source type")

    transform = transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x[:3, :, :]),
        transforms.Normalize((0.485, 0.456, 0.406),
                             (0.229, 0.224, 0.225))
    ])
    return transform(image).unsqueeze(0)


# ------------------ Denormalize for Saving ------------------
def tensor_to_pil(tensor):
    unloader = transforms.Compose([
        transforms.Normalize(mean=[0., 0., 0.],
                             std=[1/0.229, 1/0.224, 1/0.225]),
        transforms.Normalize(mean=[-0.485, -0.456, -0.406],
                             std=[1., 1., 1.])
    ])
    image = tensor.cpu().clone().squeeze(0).detach()
    image = unloader(image).clamp(0, 1)
    image = transforms.ToPILImage()(image)
    return image


# ------------------ Style Transfer Model ------------------
cnn = models.vgg19(pretrained=True).features.to(device).eval()

class ContentLoss(nn.Module):
    def __init__(self, target):
        super().__init__()
        self.target = target.detach()
    def forward(self, x):
        self.loss = nn.functional.mse_loss(x, self.target)
        return x

class StyleLoss(nn.Module):
    def __init__(self, target_feature):
        super().__init__()
        self.target = self.gram_matrix(target_feature).detach()
    def gram_matrix(self, input):
        a, b, c, d = input.size()
        features = input.view(a*b, c*d)
        G = torch.mm(features, features.t())
        return G.div(a*b*c*d)
    def forward(self, x):
        G = self.gram_matrix(x)
        self.loss = nn.functional.mse_loss(G, self.target)
        return x


def get_style_model_and_losses(cnn, style_img, content_img,
                               content_layers=['conv_4'],
                               style_layers=['conv_1','conv_2','conv_3','conv_4','conv_5']):
    import copy
    cnn = copy.deepcopy(cnn)
    content_losses = []
    style_losses = []

    model = nn.Sequential()
    i = 0
    for layer in cnn.children():
        if isinstance(layer, nn.Conv2d):
            i += 1
            name = f'conv_{i}'
        elif isinstance(layer, nn.ReLU):
            name = f'relu_{i}'
            layer = nn.ReLU(inplace=False)
        elif isinstance(layer, nn.MaxPool2d):
            name = f'pool_{i}'
        elif isinstance(layer, nn.BatchNorm2d):
            name = f'bn_{i}'
        else:
            raise RuntimeError(f'Unrecognized layer: {layer.__class__.__name__}')

        model.add_module(name, layer)

        if name in content_layers:
            target = model(content_img).detach()
            content_loss = ContentLoss(target)
            model.add_module(f"content_loss_{i}", content_loss)
            content_losses.append(content_loss)

        if name in style_layers:
            target = model(style_img).detach()
            style_loss = StyleLoss(target)
            model.add_module(f"style_loss_{i}", style_loss)
            style_losses.append(style_loss)

    for i in range(len(model) - 1, -1, -1):
        if isinstance(model[i], ContentLoss) or isinstance(model[i], StyleLoss):
            break
    model = model[:(i+1)]

    return model, style_losses, content_losses


def run_style_transfer(content_img, style_img, num_steps=200,
                       style_weight=1e6, content_weight=1):
    input_img = content_img.clone()
    model, style_losses, content_losses = get_style_model_and_losses(cnn, style_img, content_img)
    optimizer = optim.LBFGS([input_img.requires_grad_()], lr=0.1)

    print("Optimizing...")
    run = [0]

    while run[0] <= num_steps:
        def closure():
            optimizer.zero_grad()
            model(input_img)
            style_score = sum(sl.loss for sl in style_losses)
            content_score = sum(cl.loss for cl in content_losses)
            loss = style_score * style_weight + content_score * content_weight
            loss.backward()

            run[0] += 1
            if run[0] % 50 == 0:
                print(f"Step {run[0]} | Style: {style_score.item():.4f} | Content: {content_score.item():.4f}")

            return loss

        optimizer.step(closure)
        input_img.data.clamp_(0, 1)

    return input_img
