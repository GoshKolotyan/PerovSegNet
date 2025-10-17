import logging
import numpy as np
import streamlit as st

from typing import Tuple
from .model import Segmenter

class ImageProcessor:
    def __init__(self, image_bytes: str, material_selection: str = 'auto'):
        """
        Args:
            image_bytes: Path to the image file
            material_selection: How to identify material cluster
                - 'auto': Use the smaller cluster (assumes material < 50% of image)
                - 'bright': Use the brighter cluster
                - 'dark': Use the darker cluster
        """
        self.image_path = image_bytes
        self.material_selection = material_selection
        self.segmenter = self._load_segmenter(self.image_path, self.material_selection)
        self.original_image = self.segmenter.img_rgb

    @staticmethod
    @st.cache_resource
    def _load_segmenter(image_path, material_selection):
        """Load and cache the segmentation model."""
        return Segmenter(image_path, material_selection)

    # @st.cache_data(max_entries=3, ttl=AppConfig.get('CACHE_TIMEOUT'))
    def __call__(self) -> Tuple[np.ndarray, float]:
        """Main processing pipeline with caching."""
        try:
            segmenter = self.segmenter

            pixels = segmenter._load_image()

            label2d, cluster_centers = segmenter._kmeans_first_pass(
                pixels
            )
            avg_intensity = cluster_centers.flatten()
            material_cluster = np.argmax(avg_intensity)
            binary_mask = (label2d == material_cluster).astype(np.uint8)

            segmented_image_material_first = segmenter.img_rgb.copy()
            segmented_image_background_first = segmenter.img_rgb.copy()
            segmented_image_material_first[binary_mask == 0] = [0, 0, 0]
            segmented_image_background_first[binary_mask == 1] = [0, 0, 0]

            new_labels_2d = segmenter._second_segmentation(segmented_image_material_first)

            second_centers = segmenter.second_kmeans.cluster_centers_
            avg_color_intensity = np.sum(second_centers, axis=1)
            material_cluster_2 = np.argmax(avg_color_intensity)

            material_mask_2 = new_labels_2d == material_cluster_2
            segmented_image_material_second = segmented_image_material_first.copy()
            segmented_image_background_second = segmented_image_material_first.copy()
            segmented_image_material_second[~material_mask_2] = [0, 0, 0]
            segmented_image_background_second[material_mask_2] = [0, 0, 0]

            # Overlay: Start with background from first pass, then add the refined material from second pass
            # This creates a visualization showing all non-material (background) + refined material boundaries
            combined_result = segmented_image_background_first.copy()
            # Overlay the refined material segmentation from the second pass
            material_mask_second = np.any(segmented_image_material_second != [0, 0, 0], axis=-1)
            combined_result[material_mask_second] = segmented_image_material_second[material_mask_second]

            # Calculate material percentage based on ALL material from first pass (not refined second pass)
            total_pixels = segmenter.img_gray.size
            material_mask_first = np.any(segmented_image_material_first != [0, 0, 0], axis=-1)
            material_pixels = np.count_nonzero(material_mask_first)
            material_percentage = (material_pixels / total_pixels) * 100

            return combined_result, material_percentage

        except Exception as e:
            logging.error(f"Processing failed: {str(e)}")
            raise
