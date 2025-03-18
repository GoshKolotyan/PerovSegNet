import io
import os
import logging
import numpy as np
import streamlit as st

from PIL import Image
from typing import Tuple
from .model import Segmenter
from config import AppConfig

class ImageProcessor:
    def __init__(self, image_bytes: str):
        self.image_path = image_bytes
        self.segmenter = self._load_segmenter(self.image_path)
        self.original_image = self.segmenter.img_rgb

    @staticmethod
    @st.cache_resource
    def _load_segmenter(image_path):
        """Load and cache the segmentation model."""
        return Segmenter(image_path)

    # @st.cache_data(max_entries=3, ttl=AppConfig.get('CACHE_TIMEOUT'))
    def __call__(self) -> Tuple[np.ndarray, float]:
        """Main processing pipeline with caching."""
        try:
            segmenter = self.segmenter

            # Load image pixels
            pixels = segmenter._load_image()

            # First KMeans pass
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

            # Second segmentation pass
            new_labels_2d = segmenter._second_segmentation(segmented_image_material_first)

            second_centers = segmenter.second_kmeans.cluster_centers_
            avg_color_intensity = np.sum(second_centers, axis=1)
            material_cluster_2 = np.argmax(avg_color_intensity)

            material_mask_2 = new_labels_2d == material_cluster_2
            segmented_image_material_second = segmented_image_material_first.copy()
            segmented_image_background_second = segmented_image_material_first.copy()
            segmented_image_material_second[~material_mask_2] = [0, 0, 0]
            segmented_image_background_second[material_mask_2] = [0, 0, 0]

            # Combine results
            combined_background = segmented_image_background_first.copy()
            mask = np.any(segmented_image_background_second != [0, 0, 0], axis=-1)
            combined_background[mask] = segmented_image_background_second[mask]

            # Calculate percentage
            total_pixels = segmenter.img_gray.size
            mask_non_black = np.any(combined_background != [0, 0, 0], axis=-1)
            material_pixels = np.count_nonzero(mask_non_black)
            material_percentage = (material_pixels / total_pixels) * 100

            return combined_background, material_percentage

        except Exception as e:
            logging.error(f"Processing failed: {str(e)}")
            raise
