# BentoML — Evaluation

To validate this module, you will need to complete the following exercise. Please read the instructions carefully.

The exam is divided into two parts (one mandatory and one optional). You will work on a dataset concerning student admissions to universities. This dataset contains information to predict the chance of admission of a student to a university.

## Dataset Description

The variables are as follows:

- **GRE Score**: Score obtained on the GRE test (scored out of 340)  
- **TOEFL Score**: Score obtained on the TOEFL test (scored out of 120)  
- **University Rating**: University rating (scored out of 5)  
- **SOP**: Statement of Purpose (scored out of 5)  
- **LOR**: Letter of Recommendation (scored out of 5)  
- **CGPA**: Cumulative Grade Point Average (scored out of 10)  
- **Research**: Research experience (0 or 1)  
- **Chance of Admit**: Chance of admission (scored out of 1)  

---

## Exam Structure

### Part 1: Mandatory

You must complete the following steps:

1. Prepare your work environment and load the data.  
2. Create a linear regression model and test its performance.  
3. Set up a prediction API.  
4. Create a bento and containerize it with Docker.  

### Part 2: Optional

This part is **not required** for the validation of the exam.  
It allows you to practice freely by implementing a deployment case using multiple runners with BentoML and to explore a more realistic architecture.

---

# Part 1: Mandatory Part

## 1.1 Preparing the Work Environment

### Retrieving the Work Repository

First, fork the following repository:

```

[https://github.com/DataScientest-Studio/examen_bentoml](https://github.com/DataScientest-Studio/examen_bentoml)

```

Then clone your fork locally. You should obtain the following structure:

```

├── examen_bentoml
│   ├── data
│   │   ├── processed
│   │   └── raw
│   ├── models
│   ├── src
│   └── README.md

```

### Loading the Data

Download the dataset and place it into the `data/raw` folder:

```

[https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv](https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv)

````

### Creating the Virtual Environment

Create a virtual environment of your choice to work in an isolated Python environment without impacting your system installation.

---

## 1.2 Creating the Model

This step includes data preparation, modeling, and performance evaluation.  
You must:

- Split the data into training and test sets.
- Normalize the data if necessary.
- Train a regression model.
- Evaluate its performance.

### Data Preparation

Create a Python script named `prepare_data.py` inside the `src` folder.

This script must:

1. Load the dataset.  
2. Clean the data.  
3. Split it into:
   - `X_train`
   - `X_test`
   - `y_train`
   - `y_test`  
4. Save all outputs into the `data/processed` folder.

You may use **pandas** and **scikit-learn**.

The target variable is **Chance of Admit**.  
You are free to remove any features that you logically consider unnecessary.

### Modeling

Create a Python script named `train_model.py` inside the `src` folder.

This script must:

1. Load the training data.
2. Create and train a regression model.
3. Evaluate its performance on the test data.

You can use any metric you prefer:

- R²  
- RMSE  
- MAE  
- etc.

Once the model performance is satisfactory:

1. Save the trained model in the **BentoML Model Store**.
2. Verify its registration using the appropriate BentoML command.

---

## 1.3 Setting up the Prediction API

Create a Python script named `service.py` inside the `src` folder.

This script must:

1. Load the saved model from BentoML.
2. Create a secure API.
3. Serve predictions through a BentoML service.

### API Requirements

- The API must be accessible via an **HTTP POST** request.
- It must accept all necessary features as input.
- It must return the **Chance of Admit** prediction.

### Required Endpoints

- **Login endpoint**  
  Used to authenticate users (security method of your choice).

- **Predict endpoint**  
  Used to perform predictions.

You may add additional endpoints if useful.

Make sure to test the API with inference requests.

---

## 1.4 Creating a Bento & Containerization with Docker

A **bento** is an archive that contains:

- Your training code
- Your API code
- Saved models
- Dependencies
- Docker configuration

Create a file named `bentofile.yaml` at the root of your project.

Example (do **not** copy directly, adapt it):

```yaml
service:
  name: admissions_prediction
  version: 1.0.0

labels:
  owner: "DataScientest"
  project: "Admissions Prediction"
  description: "Predict the chance of admission of a student in a university"

include:
  - "*.py"

python:
  packages:
    - scikit-learn
    - pandas
````

Then:

1. Build the bento.
2. Containerize it using BentoML.
3. Create a Docker image.
4. Run it locally and test your API.

### Exporting the Docker Image

When finished, save your image using:

```bash
# BE CAREFUL to respect the naming convention
docker save -o bento_image.tar <your_name>_<your_image_name>
```

⚠️ Respect the `<your_name>_<your_image_name>` naming convention.
Incorrect naming may lead to evaluation failure.

---

## 1.5 Unit Tests

You must write unit tests to verify the service.

### JWT Authentication Tests

* Authentication fails if the JWT token is missing or invalid.
* Authentication fails if the JWT token is expired.
* Authentication succeeds with a valid JWT token.

### Login API Tests

* Valid credentials return a JWT token.
* Invalid credentials return a `401` error.

### Prediction API Tests

* Missing or invalid JWT returns `401`.
* Valid input returns a valid prediction.
* Invalid input returns an error.

You may extend these tests if needed.

---

## 1.6 Mandatory Part Deliverables

You must provide an archive containing **three deliverables**:

### Deliverable 1 — README.md

It must clearly describe:

* All commands required to:

  * Decompress the archive.
  * Load the Docker image.
  * Run the containerized API.
* The commands required to run the unit tests, all of which must return **PASSED**.

### Deliverable 2 — Docker Image Archive

* The compressed Docker image created with BentoML.

### Deliverable 3 — Pytest File

* A pytest test file that validates your API.
* All tests must return **PASSED**.

### Expected Workflow

1. Decompression of the archive
2. Loading the Docker image and starting the API
3. Running:

   ```bash
   pytest tests/XXX.py -v
   ```

   → All tests must succeed.

---

Upload your final exam archive (`.zip` or `.tar`) in the **My Exams** tab once everything works.

Congratulations. Reaching this point means you have completed the BentoML module 🎉

The optional challenge is available if you want to push the architecture further.
