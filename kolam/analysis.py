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