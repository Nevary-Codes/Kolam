import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize

def analyze_and_plot_kolam(image_path, dot_size=5, skeleton_marker_size=1, skeleton_color='gray'):
    """
    Analyze a Kolam image and plot the dots and skeleton.

    Parameters:
    - image_path: str, path to the Kolam image
    - dot_size: int, size of the dots in the output plot
    - skeleton_marker_size: int, size of skeleton points in the output plot
    - skeleton_color: str or color, color for the skeleton points
    """
    
    # 1. Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Threshold (invert if necessary)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 3. Skeletonize
    skeleton = skeletonize(binary // 255)
    
    # 4. Detect dots (lenient settings)
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 2
    params.maxArea = 1000
    params.filterByCircularity = False
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(binary)
    dots = [kp.pt for kp in keypoints]
    
    # 5. Plotting
    fig, ax = plt.subplots(figsize=(8,8))
    
    # Plot dots
    for x, y in dots:
        ax.plot(x, y, 'ko', markersize=dot_size)
    
    # Plot skeleton pixels as separate points in grey
    coords = np.column_stack(np.where(skeleton))
    ax.plot(coords[:,1], coords[:,0], '.', color=skeleton_color, markersize=skeleton_marker_size)
    
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.axis('off')
    plt.show()
    
    return dots, skeleton


import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from PIL import Image, ExifTags

def analyze_kolam_full_phone(image_path, dot_size=5, skeleton_marker_size=1, skeleton_color='gray', max_dim=1024):
    """
    Analyze a Kolam image from phone photos, displaying all intermediate steps:
    - Grayscale
    - Canny edges
    - Contours
    - Skeleton
    - Detected dots
    Handles phone orientation, adaptive thresholding, and resizing.
    """
    # 1. Load image with PIL (for EXIF orientation)
    img = Image.open(image_path)
    
    # 2. Correct orientation based on EXIF
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
    except:
        pass  # no EXIF orientation
    
    # 3. Convert to OpenCV format
    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # 4. Resize if too large
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        image = cv2.resize(image, (int(w*scale), int(h*scale)))
    
    # 5. Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 6. Canny edges
    edges = cv2.Canny(gray, 50, 150)
    
    # 7. Contours
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = np.zeros_like(gray)
    cv2.drawContours(contour_img, contours, -1, 255, 1)
    
    # 8. Adaptive thresholding and skeletonization
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11,
        C=2
    )
    skeleton = skeletonize(binary // 255)
    
    # 9. Detect dots (lenient)
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 2
    params.maxArea = 1000
    params.filterByCircularity = False
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(binary)
    dots = [kp.pt for kp in keypoints]
    
    # 10. Plot results
    fig, axes = plt.subplots(2, 3, figsize=(15,10))
    
    axes[0,0].imshow(gray, cmap='gray'); axes[0,0].set_title("Grayscale"); axes[0,0].axis('off')
    axes[0,1].imshow(edges, cmap='gray'); axes[0,1].set_title("Canny Edges"); axes[0,1].axis('off')
    axes[0,2].imshow(contour_img, cmap='gray'); axes[0,2].set_title("Contours"); axes[0,2].axis('off')
    axes[1,0].imshow(skeleton, cmap='gray'); axes[1,0].set_title("Skeleton"); axes[1,0].axis('off')
    
    axes[1,1].imshow(gray, cmap='gray')
    for x, y in dots:
        axes[1,1].plot(x, y, 'ro', markersize=dot_size)
    axes[1,1].set_title("Detected Dots"); axes[1,1].axis('off')
    
    axes[1,2].imshow(gray, cmap='gray')
    coords = np.column_stack(np.where(skeleton))
    axes[1,2].plot(coords[:,1], coords[:,0], '.', color=skeleton_color, markersize=skeleton_marker_size)
    for x, y in dots:
        axes[1,2].plot(x, y, 'ko', markersize=dot_size)
    axes[1,2].set_title("Skeleton + Dots"); axes[1,2].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return gray, edges, contour_img, skeleton, dots

# Example usage:
# gray, edges, contours, skeleton, dots = analyze_kolam_full_phone("phone_photo.jpg")
from scipy.spatial import distance
import numpy as np

def extract_features_density(gray, skeleton, dots, contours):
    """
    Extract density-based features for Kolam classification.
    """
    features = {}
    h, w = gray.shape
    area = h * w

    # Basic features
    features['num_dots'] = len(dots)
    features['skeleton_length'] = np.sum(skeleton)
    features['num_contours'] = len(contours)

    # Density-based features
    features['dot_density'] = len(dots) / area
    features['skeleton_density'] = np.sum(skeleton) / area

    # Average distance between dots (optional)
    if len(dots) > 1:
        pts = np.array(dots)
        dists = distance.pdist(pts)
        features['avg_dot_distance'] = np.mean(dists)
    else:
        features['avg_dot_distance'] = 0

    return features

def classify_kolam_density(features):
    """
    Classify Kolam based on density features.
    """
    dot_density = features['dot_density']
    skeleton_density = features['skeleton_density']

    # Thresholds (adjust based on your dataset)
    if dot_density < 0.0005 and skeleton_density < 0.002:
        return "Simple Dot-Based"
    elif dot_density < 0.002 and skeleton_density < 0.01:
        return "Geometric"
    else:
        return "Complex/Looped"
    

# Run your full analysis
gray, edges, contour_img, skeleton, dots = analyze_kolam_full_phone("Kolam Generator.png")

# Extract density features
features = extract_features_density(gray, skeleton, dots, contours=contour_img)

# Classify
kolam_class = classify_kolam_density(features)

print("Kolam classification:", kolam_class)
print("Feature details:", features)