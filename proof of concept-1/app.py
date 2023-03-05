from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import json
from json import JSONEncoder




def create_dataframe(matrix, tokens):
    doc_names = [f'doc_{i+1}' for i, _ in enumerate(matrix)]
    df = pd.DataFrame(data=matrix, index=doc_names, columns=tokens)

    return(df)


def calculate_similarity(input_text, output_text):
    count_vectorizer = CountVectorizer()
    data = [input_text, output_text]
    vector_matrix = count_vectorizer.fit_transform(data)
    tokens = count_vectorizer.get_feature_names()

    create_dataframe(vector_matrix.toarray(), tokens)
    cosine_similarity_matrix = cosine_similarity(vector_matrix)
    create_dataframe(cosine_similarity_matrix, ['input_text', 'output_text'])

    Tfidf_vect = TfidfVectorizer()
    vector_matrix = Tfidf_vect.fit_transform(data)

    tokens = Tfidf_vect.get_feature_names()
    create_dataframe(vector_matrix.toarray(), tokens)

    cosine_similarity_matrix = cosine_similarity(vector_matrix)
    df = create_dataframe(cosine_similarity_matrix, ['input_text', 'output_text'])

    # Find the row index of the highest similarity score (excluding the diagonal, which is always 1)
    max_similarity_idx = np.argmax(cosine_similarity_matrix[0, 1:]) + 1

    similar_text = data[max_similarity_idx]

    similarity_percentage = cosine_similarity_matrix[0, max_similarity_idx]

    return similar_text, similarity_percentage

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded files
        input_file = request.files['input_file']
        output_file = request.files['output_file']

        # Read the file contents
        input_text = input_file.read().decode('utf-8')
        output_text = output_file.read().decode('utf-8')

        # Get the threshold value from the form
        threshold = float(request.form.get('threshold'))

        # Check the similarity between the files
        similar_text, similarity_percentage = calculate_similarity(input_text, output_text)

        # Return the results page
        return render_template('results.html', 
            similar_text=similar_text, 
            similarity_percentage=similarity_percentage,
            threshold=threshold)

    # Render the home page template
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)