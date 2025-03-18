# PerovSegNet

**PerovSegNet** is a machine learning-based segmentation model designed for segmenting perovskite layers. It leverages advanced image processing techniques and clustering algorithms to provide accurate segmentation results.

## Installation

To install the required dependencies, run:

```sh
pip install -r app/req.txt
```

## Usage

To launch the application using Streamlit, run:

```sh
streamlit run app.py
```

## Sample Output

Here is an example of the segmentation results produced by **PerovSegNet**:


### Segmentation Output
![Original Image   Segmented Image](Img/Usage_example.jpeg)


## Features
- Image segmentation for perovskite layers
- Utilizes machine learning techniques like **KMeans Clustering**
- Built with **Streamlit** for an interactive UI
- Supports real-time visualization with **Matplotlib**

## Dependencies
PerovSegNet relies on the following libraries:
- `numpy`
- `opencv-python`
- `matplotlib`
- `scikit-learn`
- `streamlit`
- `pytest` (for testing #TODO implement logic)


## License
This project is licensed under the MIT License.

## Contact
For any inquiries or issues, please reach out via GitHub or open an issue in the repository.

