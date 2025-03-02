import cv2
import json
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

class ImageSegmenter:

    def __init__(self, image_path: str, num_clusters: int = 2):

        self.image_path = image_path
        self.num_clusters = num_clusters
        self.img_rgb = None
        self.pixels = None
        self.labels = None
        self.centroids = None
        self.semantic_labels = {}  # e.g., {0: "background", 1: "material"}
        self.cluster_counts = None
        self.segmented_img = None  # for visualization: image with centroid colors
        self.cluster_images = []   # individual cluster images
        self.annotations = {}      # internal annotation structure
        
    def load_and_preprocess_image(self):
        """Loads the image and converts it to RGB (no resizing)."""
        img = cv2.imread(self.image_path)
        if img is None:
            raise ValueError(f"Image not found: {self.image_path}")
        self.img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(f"Image loaded: {self.image_path} with dimensions {self.img_rgb.shape}")
    
    def reshape_image(self):
        if self.img_rgb is None:
            raise ValueError("Image not loaded. Call load_and_preprocess_image() first.")
        self.pixels = self.img_rgb.reshape((-1, 3)).astype(np.float32)
        print("Image reshaped to pixel array with shape:", self.pixels.shape)
    
    def perform_clustering(self):
        if self.pixels is None:
            raise ValueError("Pixel data not available. Call reshape_image() first.")
        kmeans = KMeans(n_clusters=self.num_clusters, random_state=42)
        kmeans.fit(self.pixels)
        self.labels = kmeans.labels_
        self.centroids = kmeans.cluster_centers_
        self.cluster_counts = np.bincount(self.labels)
        print("K-Means clustering performed. Cluster counts:", self.cluster_counts)
    
    def assign_semantic_labels(self):

        if self.cluster_counts is None:
            raise ValueError("Clustering must be performed first.")
        # The cluster with more pixels is considered "background"
        if self.cluster_counts[0] > self.cluster_counts[1]:
            self.semantic_labels = {0: "background", 1: "material"}
        else:
            self.semantic_labels = {0: "material", 1: "background"}
        print("Semantic labels assigned:", self.semantic_labels)
    
    def create_segmented_image(self):

        if self.labels is None or self.centroids is None:
            raise ValueError("Clustering must be performed first.")
        segmented_pixels = np.array([self.centroids[label] for label in self.labels])
        self.segmented_img = segmented_pixels.reshape(self.img_rgb.shape).astype(np.uint8)
        print("Segmented image (centroid colors) created.")
    
    def create_cluster_images(self):

        if self.labels is None:
            raise ValueError("Clustering must be performed first.")
        labels_2d = self.labels.reshape(self.img_rgb.shape[0], self.img_rgb.shape[1])
        self.cluster_images = []
        for i in range(self.num_clusters):
            cluster_img = np.zeros_like(self.img_rgb)
            cluster_img[labels_2d == i] = self.img_rgb[labels_2d == i]
            self.cluster_images.append(cluster_img)
        print("Individual cluster images created.")
    
    def generate_semantic_segmentation_mask(self):

        labels_2d = self.labels.reshape(self.img_rgb.shape[:2])
        mask = np.zeros_like(labels_2d, dtype=np.uint8)
        for i in range(self.num_clusters):
            cat_id = 1 if self.semantic_labels[i] == "background" else 2
            mask[labels_2d == i] = cat_id
        return mask
    
    def get_polygon_annotations(self, image_id: int):

        mask = self.generate_semantic_segmentation_mask()
        annotations = []
        # Process both categories: 1 (background) and 2 (material)
        for cat_id in [1, 2]:
            cat_mask = (mask == cat_id).astype(np.uint8) * 255
            contours, _ = cv2.findContours(cat_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) < 10:  # skip small areas
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)
                segmentation = cnt.flatten().tolist()
                if len(segmentation) < 6:
                    continue
                annotation = {
                    "image_id": image_id,
                    "category_id": cat_id,
                    "bbox": [x, y, w, h],
                    "area": area,
                    "segmentation": [segmentation],
                    "iscrowd": 0
                }
                annotations.append(annotation)
        return annotations
    
    def plot_results(self):
        num_subplots = self.num_clusters + 2  # Original + segmented + each cluster
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, num_subplots, 1)
        plt.imshow(self.img_rgb)
        plt.title("Original Image")
        plt.axis("off")
        
        plt.subplot(1, num_subplots, 2)
        plt.imshow(self.segmented_img)
        plt.title("Segmented Image (Centroid Colors)")
        plt.axis("off")
        
        for i, cluster_img in enumerate(self.cluster_images):
            plt.subplot(1, num_subplots, i + 3)
            plt.imshow(cluster_img)
            plt.title(f"Cluster {i} ({self.semantic_labels.get(i, 'N/A')})")
            plt.axis("off")
        
        plt.tight_layout()
        plt.show()
    
    def run(self):
        """Executes the full segmentation pipeline."""
        self.load_and_preprocess_image()
        self.reshape_image()
        self.perform_clustering()
        self.assign_semantic_labels()
        self.create_segmented_image()
        self.create_cluster_images()
        # Optionally, plot the results
        # self.plot_results()
        # Return internal annotation info (e.g., image dimensions)
        return {"image_path": self.image_path, "width": self.img_rgb.shape[1], "height": self.img_rgb.shape[0]}


def process_folder(folder_path: str, output_json: str):

    image_files = glob.glob(os.path.join(folder_path, "*.*"))
    image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    print(f"Found {len(image_files)} images in folder {folder_path}.")
    
    coco = {
        "info": {
            "description": "COCO-format semantic segmentation dataset (polygon annotations) from folder processing",
            "version": "1.0",
            "year": 2025,
            "contributor": "Gosh",
            "date_created": "2025-03-02"
        },
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": [
            {"id": 1, "name": "background", "supercategory": "none"},
            {"id": 2, "name": "material", "supercategory": "none"}
        ]
    }
    
    image_id = 1
    ann_id = 1
    
    for img_file in image_files:
        print(f"Processing image: {img_file}")
        segmenter = ImageSegmenter(image_path=img_file, num_clusters=2)
        img_info = segmenter.run()  # Run segmentation pipeline
        width = img_info["width"]
        height = img_info["height"]
        file_name = os.path.basename(img_file)
        
        coco["images"].append({
            "id": image_id,
            "width": width,
            "height": height,
            "file_name": file_name
        })
        
        ann_list = segmenter.get_polygon_annotations(image_id)
        for ann in ann_list:
            # Assign a unique annotation id
            ann["id"] = ann_id
            coco["annotations"].append(ann)
            ann_id += 1
        
        image_id += 1
        print("Image {} is processed".format(img_file))
    
    with open(output_json, 'w') as f:
        json.dump(coco, f, indent=4)
    print(f"COCO annotation for folder saved to {output_json}")


if __name__ == "__main__":
    folder_path = "../Data"  
    output_annotation_file = "../Data/coco_folder_annotation.json"
    process_folder(folder_path, output_annotation_file)
