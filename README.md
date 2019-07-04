# Bug classifier

## About
* A small api which uses a pre-calculated model to make predictions.
* The notebook `bug-classifier.ipynb` shows how I trained the model.
* The purpose of this project was to gain some experience using fast.ai.
* For more information see fast.ai lesson 2 [here](https://github.com/fastai/course-v3/blob/master/nbs/dl1/lesson2-download.ipynb).

### Requirements

* [Docker](https://www.docker.com/)

### Installation

#### Api
```bash
// build and run app
./gradlew build run

// stop app
./gradlew stop
```

#### Notebook

You will need access to a GPU to run the jupyter notebook. 
Fast.ai recommend using a `p2.xlarge` instance.
Follow the installation guide [here](https://course.fast.ai/start_aws.html).

## Usage

```bash
localhost:8000
```