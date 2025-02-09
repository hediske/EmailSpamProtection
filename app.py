import pickle
import streamlit as st 

def main():
    with open('./models/logistic_regression.pkl','rb') as file:
        model = pickle.load(file)
    with open('./models/tfid_vectorizer.pkl','rb') as file:
        vectorizer = pickle.load(file)
    st.title("Spam Detection App using a logistic Regression Model")
    st.subheader("Enter the message to check if it is spam or not")
    message = st.text_area("Enter the message")
    if st.button("Predict"):
        message = [message]
        message_vect = vectorizer.transform(message)
        prediction = model.predict(message_vect)
        if prediction[0] == 1:
            st.success("The message is not a spam")
        else:
            st.error("The message is a spam")


main()
    