#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>
#include <vector>
#include <cstdio>

using namespace cv;
using namespace std;

class Segmenter {
public:
    string imagePath;
    Mat img;
    int K = 2;
    Segmenter(const string &path) : imagePath(path) {
        img = imread(imagePath, IMREAD_COLOR);
        if (img.empty()) {
            cerr << "Error: Unable to load image " << imagePath << endl;
            exit(1);
        }
    }

    Mat loadImage() {
        Mat data = img.reshape(1, img.rows * img.cols);
        data.convertTo(data, CV_32F);
        return data;
    }

    void runKMeans(const Mat &data, Mat &labels, Mat &centers) {
        TermCriteria criteria(TermCriteria::EPS + TermCriteria::COUNT, 10, 1.0);
        kmeans(data, K, labels, criteria, 10, KMEANS_RANDOM_CENTERS, centers);
    }
    void plot(const Mat &binaryMask, double materialPercentage, double backgroundPercentage) {
        Mat segmentedImageMaterial = img.clone();
        Mat segmentedImageBackground = img.clone();

        for (int i = 0; i < img.rows; i++) {
            for (int j = 0; j < img.cols; j++) {
                if (binaryMask.at<uchar>(i, j) == 255) {
                    segmentedImageMaterial.at<Vec3b>(i, j) = Vec3b(0, 0, 0);
                } else {
                    segmentedImageBackground.at<Vec3b>(i, j) = Vec3b(0, 0, 0);
                }
            }
        }

        int width = img.cols;
        int height = img.rows;
        Mat combined(height, width * 3, img.type());

        img.copyTo(combined(Rect(0, 0, width, height)));
        segmentedImageMaterial.copyTo(combined(Rect(width, 0, width, height)));
        segmentedImageBackground.copyTo(combined(Rect(width * 2, 0, width, height)));

        int fontFace = FONT_HERSHEY_SIMPLEX;
        double fontScale = 0.8;
        int thickness = 2;
        int baseline = 0;
        string text;

        text = "Original Image";
        Size textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
        Point textOrg((width - textSize.width) / 2, textSize.height + 5);
        putText(combined(Rect(0, 0, width, height)), text, textOrg, fontFace, fontScale, Scalar(0, 255, 0), thickness);

        text = "Material Segmentation";
        textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
        textOrg = Point(width + (width - textSize.width) / 2, textSize.height + 5);
        putText(combined(Rect(width, 0, width, height)), text, textOrg, fontFace, fontScale, Scalar(0, 255, 0), thickness);

        char buffer[100];
        snprintf(buffer, sizeof(buffer), "Material: %.2f%%", materialPercentage);
        text = buffer;
        textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
        textOrg = Point(width + (width - textSize.width) / 2, textSize.height + 30);
        putText(combined(Rect(width, 0, width, height)), text, textOrg, fontFace, fontScale, Scalar(0, 255, 0), thickness);

        snprintf(buffer, sizeof(buffer), "Background: %.2f%%", backgroundPercentage);
        text = buffer;
        textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
        textOrg = Point(width + (width - textSize.width) / 2, textSize.height + 55);
        putText(combined(Rect(width, 0, width, height)), text, textOrg, fontFace, fontScale, Scalar(0, 255, 0), thickness);

        text = "Background Segmentation";
        textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
        textOrg = Point(width * 2 + (width - textSize.width) / 2, textSize.height + 5);
        putText(combined(Rect(width * 2, 0, width, height)), text, textOrg, fontFace, fontScale, Scalar(0, 255, 0), thickness);

        snprintf(buffer, sizeof(buffer), "Material: %.2f%%", materialPercentage);
        text = buffer;
        textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
        textOrg = Point(width * 2 + (width - textSize.width) / 2, textSize.height + 30);
        putText(combined(Rect(width * 2, 0, width, height)), text, textOrg, fontFace, fontScale, Scalar(0, 255, 0), thickness);

        snprintf(buffer, sizeof(buffer), "Background: %.2f%%", backgroundPercentage);
        text = buffer;
        textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
        textOrg = Point(width * 2 + (width - textSize.width) / 2, textSize.height + 55);
        putText(combined(Rect(width * 2, 0, width, height)), text, textOrg, fontFace, fontScale, Scalar(0, 255, 0), thickness);

        double scaleFactor = 0.1;  // Now 0.1 is best.
        Mat combinedResized;
        resize(combined, combinedResized, Size(), scaleFactor, scaleFactor);

        namedWindow("Segmentation", WINDOW_NORMAL);
        imshow("Segmentation", combinedResized);
        waitKey(0);
    }

    void operator()() {
        Mat data = loadImage();

        Mat labels, centers;
        runKMeans(data, labels, centers);

        Mat label2d = labels.reshape(1, img.rows);

        vector<double> sums;
        for (int i = 0; i < centers.rows; i++) {
            double sum = centers.at<float>(i, 0) +
                         centers.at<float>(i, 1) +
                         centers.at<float>(i, 2);
            sums.push_back(sum);
        }
        int material_cluster = (sums[0] < sums[1]) ? 1 : 0;

        Mat binaryMask(img.rows, img.cols, CV_8U, Scalar(0));
        for (int i = 0; i < label2d.rows; i++) {
            for (int j = 0; j < label2d.cols; j++) {
                int label = label2d.at<int>(i, j);
                if (label == material_cluster) {
                    binaryMask.at<uchar>(i, j) = 255;
                }
            }
        }

        int totalPixels = img.rows * img.cols;
        int materialPixels = countNonZero(binaryMask);
        int backgroundPixels = totalPixels - materialPixels;
        double materialPercentage = (materialPixels / (double)totalPixels) * 100.0;
        double backgroundPercentage = (backgroundPixels / (double)totalPixels) * 100.0;

        plot(binaryMask, materialPercentage, backgroundPercentage);
    }
};

int main() {
    string imagePath = "../Data/D32_n21_x50_A.jpg";
    Segmenter segmenter(imagePath);
    segmenter();  
    return 0;
}
