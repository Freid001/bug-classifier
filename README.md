# Bug classifier

## About
* A small api which uses a pre-calculated model to classify bug images.
* The notebook `bug-classifier.ipynb` shows how I trained the model.
* The model `bug.pkl` classifies an image into a single category: `ant`, `bee`, `moth`, `wasp`.
* The model `bug-multi.pkl` classifies an image into multiple categories: `ant`, `bee`, `flower`, `leaf`, `honeycomb`.
* The purpose of this project was to gain some experience using fast.ai.
* For more information see fast.ai lessons: 1,2 and 3 [here](https://course.fast.ai/).

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

### User interface
```bash
// classify a image file
localhost:8000/upload

// classify a url
localhost:8000/url
```

### Api

##### GET /api/schema

##### Returns

```json
{
    "openapi": "3.0.0",
    "info": {
        "title": "App",
        "version": "1.0"
    },
    "servers": [
        {
            "url": "http://localhost:{port}",
            "variables": {
                "port": {
                  "default": "8000"
                }
            }
        }
    ],
    "schemas": {
        "Classify": {
            "type": "object",
            "properties": {
                "classified": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "probability": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
                }
            }
        },
        "ErrorMessage": {
            "type": "object",
                "properties": {
                "message": {
                    "type": "string"
                }
            }
        },
        "Errors": {
            "type": "array",
            "items": {
                "$ref": "#/schemas/ErrorMessage"
            }
        }
    },
    "paths": {
        "/api/classify": {
            "get": {
                "summary": "Classify an image by url.",
                "parameters": [{
                    "name": "url",
                    "description": "Url of image.",
                    "in": "query",
                    "schema": {
                        "type": "string"
                    },
                    "required": true
                }],
                "responses": {
                    "200": {
                        "description": "ok",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/schemas/Classify"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/schemas/Errors"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

##### GET /api/classify?url={url}

##### Returns

```json

{
    "classified": [
      "ant"
    ],
    "probability": [
      0.9990659356117249
    ]
}
```

##### POST /api/classify
