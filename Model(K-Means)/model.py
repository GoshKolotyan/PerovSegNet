import cv2
import numpy as np 
import matplotlib.pyplot as plt 
from sklearn.cluster import KMeans

class Segmenter:
    def __init__(self, image_path): 
        self.image_path = image_path
        self.img = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
        self.kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)

    def _load_image(self, image_path):
        return cv2.imread(image_path).reshape((-1, 3))
    
    def _kmeans(self, pixels):
        self.kmeans.fit(pixels)
        labels = self.kmeans.labels_
        labels_2d = labels.reshape((self.img.shape[0], self.img.shape[1]))
        cluster_centers = self.kmeans.cluster_centers_
        return labels_2d, cluster_centers
    
    def _plot(self, binary_mask, material_percentage, background_percentage):
        segmented_image_material = self.img.copy()
        segmented_image_background = self.img.copy()

        segmented_image_material[binary_mask == 1] = [0, 0, 0]
        segmented_image_background[binary_mask == 0] = [0, 0, 0]

        plt.figure(figsize=(12, 6))

        plt.subplot(1, 3, 1)
        plt.imshow(self.img)
        plt.title("Original Image")
        plt.axis('off')

        plt.subplot(1, 3, 2)
        plt.imshow(segmented_image_material)
        plt.title(f"Material Segmentation\nMaterial: {material_percentage:.2f}% | Background: {background_percentage:.2f}%")
        plt.axis('off')

        plt.subplot(1, 3, 3)
        plt.imshow(segmented_image_background)
        plt.title(f"Background Segmentation\nMaterial: {material_percentage:.2f}% | Background: {background_percentage:.2f}%")
        plt.axis('off')

        plt.tight_layout()
        plt.show()

    def __call__(self):
        pixels = self._load_image(self.image_path)
        label2d, cluster_centers = self._kmeans(pixels)

        avg_intensity = np.sum(cluster_centers, axis=1)
        sorted_indices = np.argsort(avg_intensity)

        material_cluster = sorted_indices[1]

        binary_mask = np.where(label2d == material_cluster, 1, 0)

        total_pixels = self.img.shape[0] * self.img.shape[1]
        material_pixels = np.sum(binary_mask == 1)
        background_pixels = np.sum(binary_mask == 0)
        material_percentage = (material_pixels / total_pixels) * 100
        background_percentage = (background_pixels / total_pixels) * 100

        self._plot(binary_mask=binary_mask, 
                   material_percentage=material_percentage,
                   background_percentage=background_percentage)

if __name__ == '__main__':
    vle = Segmenter(image_path="../Data/D32_n21_x50_A.jpg")
    vle()
