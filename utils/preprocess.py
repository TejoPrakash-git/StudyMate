import re
import string
import unicodedata
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK resources (uncomment if needed)
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

# Text preprocessing utilities for StudyMateZ

def clean_text(text):
    """Clean text by removing special characters, extra whitespace, etc.
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def remove_stopwords(text, language='english'):
    """Remove stopwords from text.
    
    Args:
        text (str): Input text
        language (str): Language for stopwords (default: 'english')
        
    Returns:
        str: Text with stopwords removed
    """
    if not text or not isinstance(text, str):
        return ""
    
    try:
        stop_words = set(stopwords.words(language))
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
        return ' '.join(filtered_text)
    except Exception as e:
        print(f"Error removing stopwords: {str(e)}")
        return text

def lemmatize_text(text):
    """Lemmatize text to reduce words to their base form.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Lemmatized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    try:
        lemmatizer = WordNetLemmatizer()
        word_tokens = word_tokenize(text)
        lemmatized_text = [lemmatizer.lemmatize(word) for word in word_tokens]
        return ' '.join(lemmatized_text)
    except Exception as e:
        print(f"Error lemmatizing text: {str(e)}")
        return text

def split_into_sentences(text):
    """Split text into sentences.
    
    Args:
        text (str): Input text
        
    Returns:
        list: List of sentences
    """
    if not text or not isinstance(text, str):
        return []
    
    try:
        return sent_tokenize(text)
    except Exception as e:
        print(f"Error splitting into sentences: {str(e)}")
        return [text]

def extract_keywords(text, num_keywords=10):
    """Extract keywords from text based on frequency.
    
    Args:
        text (str): Input text
        num_keywords (int): Number of keywords to extract (default: 10)
        
    Returns:
        list: List of keywords
    """
    if not text or not isinstance(text, str):
        return []
    
    try:
        # Clean and tokenize text
        cleaned_text = clean_text(text)
        word_tokens = word_tokenize(cleaned_text.lower())
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in word_tokens if word not in stop_words and len(word) > 2]
        
        # Count word frequencies
        word_freq = {}
        for word in filtered_words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:num_keywords]]
    except Exception as e:
        print(f"Error extracting keywords: {str(e)}")
        return []

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks of specified size.
    
    Args:
        text (str): Input text
        chunk_size (int): Size of each chunk in characters (default: 1000)
        overlap (int): Overlap between chunks in characters (default: 200)
        
    Returns:
        list: List of text chunks
    """
    if not text or not isinstance(text, str):
        return []
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Find the end of the chunk
        end = start + chunk_size
        
        # If we're not at the end of the text, try to find a sentence boundary
        if end < len(text):
            # Look for a period, question mark, or exclamation point followed by a space or newline
            next_period = text.find('. ', end - 50, end + 50)
            next_question = text.find('? ', end - 50, end + 50)
            next_exclamation = text.find('! ', end - 50, end + 50)
            next_newline = text.find('\n', end - 50, end + 50)
            
            # Find the closest sentence boundary
            boundaries = [b for b in [next_period, next_question, next_exclamation, next_newline] if b != -1]
            
            if boundaries:
                end = min(boundaries) + 2  # +2 to include the punctuation and space
        
        # Add the chunk to our list
        chunks.append(text[start:end])
        
        # Move the start position, accounting for overlap
        start = end - overlap
    
    return chunks

def normalize_text_for_embedding(text):
    """Normalize text specifically for embedding generation.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Normalized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()