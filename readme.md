# Flask Wikipedia Search Analyzer

The Flask Wikipedia Search Analyzer is a web application that allows users to perform word frequency analysis on Wikipedia articles based on a specified topic. The application also maintains a search history with details of past searches.

## Table of Contents

- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Endpoints](#endpoints)
  - [1. Word Frequency Analysis](#1-word-frequency-analysis)
  - [2. Search History](#2-search-history)
- [Examples](#examples)

## Setup

### Prerequisites

Before setting up the application, ensure you have the following installed on your machine:

- [Python](https://www.python.org/) (version 3.6 or higher)
- [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer)
- [virtualenv](https://pypi.org/project/virtualenv/) (recommended for creating isolated Python environments)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/akshayaminupala/wikipedia_api.git
   ```


2. **Navigate to the Directory**

    ```bash
   cd your-repo
   ```


3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```


    
### Running the application 
```
 python assignment.py
```

        

### 1. Word Frequency Analysis

- **Endpoint:** `/word_frequency`
- **Method:** `GET`
- **Parameters:**
  - `topic` (required): The topic for which you want to perform word frequency analysis.
  - `n` (required): The number of top words to retrieve (positive integer).

#### Example Usage:

```bash
http://localhost:5000/word_frequency?topic=Python&n=5
```
### 2. Search History

The Search History endpoint allows you to retrieve a list of past search entries along with the top words associated with each search.

- **Endpoint:** `/search_history`
- **Method:** `GET`
- **Response Format:** JSON

### Example Usage:

```bash
http://localhost:5000/search_history
```
### Examples

shown in the demo video


