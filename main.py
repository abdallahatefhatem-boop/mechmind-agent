from IPython.display import Image, display
from langgraph.graph import END, START, StateGraph
from src.pipeline.graph import workflow
# 1. Define your graph and compile it
  # Replace State with your defined state class
# ... add nodes and edges ...
app = workflow

# 2. Generate and save the PNG image
image_bytes = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(image_bytes)