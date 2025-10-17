import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


class Segmenter:
    def __init__(self, image_path, material_selection='auto'):
        """
        Args:
            image_path: Path to the image file
            material_selection: How to identify material cluster in first pass
                - 'auto': Use the smaller cluster (assumes material < 50% of image)
                - 'bright': Use the brighter cluster
                - 'dark': Use the darker cluster
        """
        self.image_path = image_path
        self.material_selection = material_selection

        self.img_rgb = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
        self.img_gray = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)

        self.first_kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)
        self.second_kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)

    def _load_image(self):
        """Prepares grayscale image for the first segmentation pass."""
        return self.img_gray.reshape((-1, 1))

    def _kmeans_first_pass(self, pixels):
        """
        Runs the first K-Means on the grayscale pixels.
        Returns the 2D label array and cluster centers.
        """
        self.first_kmeans.fit(pixels)
        labels = self.first_kmeans.labels_
        labels_2d = labels.reshape(self.img_gray.shape)
        cluster_centers = self.first_kmeans.cluster_centers_
        return labels_2d, cluster_centers

    def _plot_first_pass(
        self,
        segmented_image_material,
        segmented_image_background,
        material_percentage,
        background_percentage,
    ):
        """Plots results of the first segmentation."""
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 3, 1)
        plt.imshow(self.img_rgb)
        plt.title("Original Image")
        plt.axis("off")

        plt.subplot(1, 3, 2)
        plt.imshow(segmented_image_material)
        plt.title(
            f"Material Segmentation\nMaterial: {material_percentage:.2f}% | Background: {background_percentage:.2f}%"
        )
        plt.axis("off")

        plt.subplot(1, 3, 3)
        plt.imshow(segmented_image_background)
        plt.title(
            f"Background Segmentation\nMaterial: {material_percentage:.2f}% | Background: {background_percentage:.2f}%"
        )
        plt.axis("off")

        plt.tight_layout()
        plt.show()

    def _second_segmentation(self, segmented_image_material):

        flat_img = segmented_image_material.reshape((-1, 3))
        non_black_mask = np.any(flat_img != [0, 0, 0], axis=1)

        material_only_pixels = flat_img[non_black_mask]

        self.second_kmeans.fit(material_only_pixels)
        second_labels = self.second_kmeans.labels_

        new_labels_full = np.zeros((len(flat_img),), dtype=np.int32)
        new_labels_full[non_black_mask] = second_labels

        new_labels_2d = new_labels_full.reshape(segmented_image_material.shape[:2])
        return new_labels_2d

    def _save_image_(self, combined_background, material_percentage):
        plt.imshow(combined_background)
        plt.title(f"Overlay: Material Al {material_percentage:.2f}%")
        plt.axis("off")
        plt.tight_layout()

        save_dir = "Predictions"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        filename = os.path.basename(self.image_path)[:-4] + "_percentage.png"
        save_path = os.path.join(save_dir, filename)

        plt.savefig(save_path)
        print(f"Saved in {save_path}")

        plt.close()


    def _plot_second_pass(
        self,
        segmented_image_background_first,
        segmented_image_background_second,
    ):
        def overlay_images(pass1_image, pass2_image):
            combined = pass1_image.copy()
            mask = np.any(pass2_image != [0, 0, 0], axis=-1)
            combined[mask] = pass2_image[mask]
            return combined

        combined_background = overlay_images(
            segmented_image_background_first, segmented_image_background_second
        )
        total_pixels = self.img_gray.size
        mask_non_black = np.any(combined_background != [0, 0, 0], axis=-1)
        material_pixels = np.count_nonzero(mask_non_black)
        material_percentage = (material_pixels / total_pixels) * 100

        plt.figure(figsize=(16, 10))

        plt.subplot(1, 2, 1)
        plt.imshow(self.img_rgb)
        plt.title("Original Img")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.imshow(combined_background)
        plt.title(f"Overlay: Materiall Al {material_percentage:.2f}%")
        plt.axis("off")
        plt.tight_layout()
        plt.show()

        self._save_image_(combined_background=combined_background, 
                          material_percentage=material_percentage)

    def __call__(self):
        pixels = self._load_image()
        label2d, cluster_centers = self._kmeans_first_pass(pixels)

        # Select which cluster represents the material
        if self.material_selection == 'auto':
            # Use the smaller cluster (assumes material is minority)
            cluster_0_count = np.sum(label2d == 0)
            cluster_1_count = np.sum(label2d == 1)
            material_cluster = 0 if cluster_0_count < cluster_1_count else 1
        elif self.material_selection == 'bright':
            # Use the brighter cluster
            avg_intensity = cluster_centers.flatten()
            material_cluster = np.argmax(avg_intensity)
        elif self.material_selection == 'dark':
            # Use the darker cluster
            avg_intensity = cluster_centers.flatten()
            material_cluster = np.argmin(avg_intensity)
        else:
            raise ValueError(f"Invalid material_selection: {self.material_selection}")

        binary_mask = (label2d == material_cluster).astype(np.uint8)

        segmented_image_material_first = self.img_rgb.copy()
        segmented_image_background_first = self.img_rgb.copy()

        # binary_mask == 1 means material (brighter cluster)
        # binary_mask == 0 means background (darker cluster)
        segmented_image_material_first[binary_mask == 0] = [0, 0, 0]  # Remove background pixels
        segmented_image_background_first[binary_mask == 1] = [0, 0, 0]  # Remove material pixels

        new_labels_2d = self._second_segmentation(segmented_image_material_first)

        second_centers = self.second_kmeans.cluster_centers_

        avg_color_intensity = np.sum(second_centers, axis=1)
        material_cluster_2 = np.argmax(avg_color_intensity)

        segmented_image_material_second = segmented_image_material_first.copy()
        segmented_image_background_second = segmented_image_material_first.copy()

        material_mask_2 = new_labels_2d == material_cluster_2
        segmented_image_material_second[~material_mask_2] = [0, 0, 0]

        segmented_image_background_second[material_mask_2] = [0, 0, 0]

        self._plot_second_pass(
            segmented_image_background_first=segmented_image_background_first,
            segmented_image_background_second=segmented_image_background_second,
        )
        
