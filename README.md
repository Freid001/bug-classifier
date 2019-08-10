# Bug classifier

## About
* A small api which uses a pre-calculated model to classify bug images.
* The notebook `bug-classifier.ipynb` shows how I trained the model.
* The model `bug.pkl` classifies an image into a single category: `ant`, `bee`, `moth`, `wasp`.
* The model `bug-multi.pkl` classifies an image into multiple categories: `ant`, `bee`, `flower`, `leaf`, `honeycomb`.
* The purpose of this project was to gain some experience using fast.ai.
* For more information see fast.ai lessons: 1,2 and 3 [here](https://course.fast.ai/).

![screen1](img/screen1.png)

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
        },
        "ImageData": {
            "type": "object",
            "properties": {
                "image_data": {
                  "type": "string"
                }
            }
        }
    },
    "paths": {
        "/api/classify": {
            "get": {
                "summary": "Classify an image by url.",
                "parameters": [
                    {
                        "name": "url",
                        "description": "Url of image.",
                        "in": "query",
                        "schema": {
                            "type": "string"
                        },
                        "required": true
                    }
                ],
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
            },
            "post": {
                "summary": "Classify an base64 image.",
                "requestBody": {
                "required": true,
                "content": {
                    "application/json": {
                            "schema": {
                                "$ref": "#/schemas/ImageData"
                            }
                        }
                    }
                },
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

###### Returns

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

###### body
```json
{
    "image_data": "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"
}
```

###### Returns

```json
{
    "classified": [
        "leaf"
    ],
    "probability": [
        0.9772832989692688
    ]
}
```