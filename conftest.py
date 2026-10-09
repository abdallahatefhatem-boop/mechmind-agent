import sys
import os

# Add the project root to sys.path so pytest can discover the 'src' module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
