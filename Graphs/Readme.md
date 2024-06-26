# Percy Jackson Character Analysis

This project analyzes the importance and interactions of characters throughout the Percy Jackson series by Rick Riordan. Using web scraping and natural language processing techniques, we extract, analyze, and visualize the relationships between characters.

## Table of Contents
- [Introduction](#introduction)
- [Data Collection](#data-collection)
- [Data Processing](#data-processing)
- [Graph Analysis](#graph-analysis)
- [Results](#results)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
The Percy Jackson series is a popular children's book series that features a rich tapestry of characters and their interactions. This project aims to provide insights into the importance of these characters by analyzing their interactions across the series.

## Data Collection
We collected data on important characters from Rick Riordan's website using BeautifulSoup for web scraping. This approach was chosen to improve Named Entity Recognition (NER) accuracy, as the raw NER model did not perform effectively on its own.

## Data Processing
The following steps were undertaken to process the data:
1. **Scraping:** Collected character information from Rick Riordan's website.
2. **Parsing Books:** Parsed all the books in the Percy Jackson series to extract interactions between characters.
3. **Extracting Relationships:** Identified and extracted relationships between characters.

## Graph Analysis
The extracted relationships were stored as graphs in the `html_files` directory. These graphs represent the interactions between characters and allow for visual analysis of character importance and connectivity.

## Results
The results of the analysis, including the visualized graphs of character interactions, can be found in the `html_files` directory. These graphs provide insights into the central characters and their roles within the series.

## Usage
To run the project, follow these steps:
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/percy-jackson-character-analysis.git
    cd percy-jackson-character-analysis
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the Jupyter notebooks for scraping, parsing, and analysis:
    ```bash
    jupyter notebook
    ```
4. Open and execute the following notebooks in order:
    - `knowledge_graph.ipynb`
    - `percy_app.ipynb`

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) document for more details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


[View the HTML file](https://raw.githack.com/Yashvishe13/Gen-AI/main/Graphs/html_files/battle_of_the_labyrinthcommunity.html)
