import tkinter as tk
from tkinterweb import HtmlFrame
import markdown

def load_md_file(file_path):
    with open(file_path, 'r') as f:
        md_content = f.read()
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content)
    return html_content

def display_md_in_window(file_path):
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Markdown Viewer")
    
    # Create an HtmlFrame to display the HTML content
    html_frame = HtmlFrame(root, width=800, height=600)
    html_frame.pack(fill="both", expand=True)
    
    # Load and display the Markdown file as HTML
    html_content = load_md_file(file_path)
    
    # Add custom CSS to style the HTML content
    css = """
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;  /* Set font to Courier New */
            background-color: #2e2e2e;  /* Dark grey background */
            color: #32cd32;  /* Green text color */
            margin: 20px;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #32cd32;  /* Black color for headings */
        }
        p {
            font-size: 14px;  /* Adjust paragraph font size */
        }
        a {
            color: #32cd32;  /* Green links */
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;  /* Underline links on hover */
        }
    </style>
    """
    
    # Combine CSS with the HTML content
    styled_html_content = css + html_content
    
    # Load the styled HTML into the HtmlFrame
    html_frame.load_html(styled_html_content)
    
    # Run the Tkinter main loop
    root.mainloop()

# Call the function with your markdown file path
display_md_in_window('README.md')


