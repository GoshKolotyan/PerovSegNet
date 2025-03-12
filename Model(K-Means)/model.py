import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

class Segmenter:
    def __init__(self, image_path, bloored=False): 
        self.image_path = image_path
        
        # Keep a reference to the full-color image (for the first segmentation)
        self.img_rgb = cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB)
        self.img_gray = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        
        self.bloored = bloored
        
        self.first_kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)
        self.second_kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)

    def _load_image(self):
        """Prepares grayscale image for the first segmentation pass."""
        if self.bloored:
            # Blur before reshaping
            self.img_gray = cv2.blur(self.img_gray, (5, 5))
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

    def _plot_first_pass(self, segmented_image_material, segmented_image_background, material_percentage, background_percentage):
        """Plots results of the first segmentation."""
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 3, 1)
        plt.imshow(self.img_rgb)
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

    def _second_segmentation(self, segmented_image_material):
        """
        Perform a second K-Means on the material-segmented image (RGB).
        The background is [0, 0, 0], so we only cluster on the non-black pixels.
        Returns:
          new_labels_2d (np.ndarray): The label map for the second pass.
        """
        # Flatten the image to (N, 3) but only keep non-black pixels
        flat_img = segmented_image_material.reshape((-1, 3))
        non_black_mask = np.any(flat_img != [0, 0, 0], axis=1)
        
        # Extract just the material region for the second pass
        material_only_pixels = flat_img[non_black_mask]
        
        # Fit second K-Means on the material region
        self.second_kmeans.fit(material_only_pixels)
        second_labels = self.second_kmeans.labels_
        
        # Create a label array the same size as the flattened image
        new_labels_full = np.zeros((len(flat_img),), dtype=np.int32) 
        # Fill in cluster labels only for the region that isn't black
        new_labels_full[non_black_mask] = second_labels
        
        # Reshape to 2D for visualization
        new_labels_2d = new_labels_full.reshape(segmented_image_material.shape[:2])
        return new_labels_2d
    def _plot_second_pass(self, 

                          segmented_image_background_first, 
                          segmented_image_background_second, 
                        ):
        def overlay_images(pass1_image, pass2_image):
            combined = pass1_image.copy()
            mask = np.any(pass2_image != [0, 0, 0], axis=-1)
            combined[mask] = pass2_image[mask]
            return combined

        combined_background = overlay_images(segmented_image_background_first, 
                                             segmented_image_background_second)
        total_pixels = self.img_gray.size
        mask_non_black = np.any(combined_background != [0, 0, 0], axis=-1)
        material_pixels = np.count_nonzero(mask_non_black)
        material_percentage = (material_pixels / total_pixels) * 100

        plt.figure(figsize=(16, 10))

        plt.subplot(1, 2, 1)
        plt.imshow(self.img_rgb)
        plt.title("Original Img")
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(combined_background)
        plt.title(f"Overlay: Materiall Al {material_percentage:.2f}%")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def __call__(self):
        pixels = self._load_image()
        label2d, cluster_centers = self._kmeans_first_pass(pixels)

        avg_intensity = cluster_centers.flatten()
        material_cluster = np.argmax(avg_intensity)

        binary_mask = (label2d == material_cluster).astype(np.uint8)

        segmented_image_material_first = self.img_rgb.copy()
        segmented_image_background_first = self.img_rgb.copy()

        segmented_image_material_first[binary_mask == 0] = [0, 0, 0]
        segmented_image_background_first[binary_mask == 1] = [0, 0, 0]


        new_labels_2d = self._second_segmentation(segmented_image_material_first)


        second_centers = self.second_kmeans.cluster_centers_

        avg_color_intensity = np.sum(second_centers, axis=1)
        material_cluster_2 = np.argmax(avg_color_intensity)

        segmented_image_material_second = segmented_image_material_first.copy()
        segmented_image_background_second = segmented_image_material_first.copy()


        material_mask_2 = (new_labels_2d == material_cluster_2)
        segmented_image_material_second[~material_mask_2] = [0, 0, 0]

        segmented_image_background_second[material_mask_2] = [0, 0, 0]

        self._plot_second_pass(
            segmented_image_background_first=segmented_image_background_first,
            segmented_image_background_second=segmented_image_background_second,)

if __name__ == '__main__':
    vle = Segmenter(image_path="../Data/A2_n4_x5.jpg", bloored=True)
    vle()
