import gradio as gr
from download_new_papers import get_papers


categories = {
    "Physics": "",
    "Mathematics": "math",
    "Computer Science": "cs",
    "Quantitative Biology": "q-bio",
    "Quantitative Finance": "q-fin",
    "Statistics": "stat",
    "Electrical Engineering and Systems Science": "eess",
    "Economics": "econ"
}

physics_categories = {
    "Astrophysics": "astro-ph",
    "Condensed Matter": "cond-mat",
    "General Relativity and Quantum Cosmology": "gr-qc",
    "High Energy Physics - Experiment": "hep-ex",
    "High Energy Physics - Lattice": "hep-lat",
    "High Energy Physics - Phenomenology": "hep-ph",
    "High Energy Physics - Theory": "hep-th",
    "Mathematical Physics": "math-ph",
    "Nonlinear Sciences": "nlin",
    "Nuclear Experiment": "nucl-ex",
    "Nuclear Theory": "nucl-th",
    "Physics": "physics",
    "Quantum Physics": "quant-ph"
}

subcategories = {
    "Astrophysics": ["Astrophysics of Galaxies", "Cosmology and Nongalactic Astrophysics", "Earth and Planetary Astrophysics", "High Energy Astrophysical Phenomena", "Instrumentation and Methods for Astrophysics", "Solar and Stellar Astrophysics"],
    "Condensed Matter": ["Disordered Systems and Neural Networks", "Materials Science", "Mesoscale and Nanoscale Physics", "Other Condensed Matter", "Quantum Gases", "Soft Condensed Matter", "Statistical Mechanics", "Strongly Correlated Electrons", "Superconductivity"],
    "General Relativity and Quantum Cosmology": ["None"],
    "High Energy Physics - Experiment": ["None"],
    "High Energy Physics - Lattice": ["None"],
    "High Energy Physics - Phenomenology": ["None"],
    "High Energy Physics - Theory": ["None"],
    "Mathematical Physics": ["None"],
    "Nonlinear Sciences": ["Adaptation and Self-Organizing Systems", "Cellular Automata and Lattice Gases", "Chaotic Dynamics", "Exactly Solvable and Integrable Systems", "Pattern Formation and Solitons"],
    "Nuclear Experiment": ["None"],
    "Nuclear Theory": ["None"],
    "Physics": ["Accelerator Physics", "Applied Physics", "Atmospheric and Oceanic Physics", "Atomic and Molecular Clusters", "Atomic Physics", "Biological Physics", "Chemical Physics", "Classical Physics", "Computational Physics", "Data Analysis, Statistics and Probability", "Fluid Dynamics", "General Physics", "Geophysics", "History and Philosophy of Physics", "Instrumentation and Detectors", "Medical Physics", "Optics", "Physics and Society", "Physics Education", "Plasma Physics", "Popular Physics", "Space Physics"],
    "Quantum Physics": ["None"],
    "Mathematics": ["Algebraic Geometry", "Algebraic Topology", "Analysis of PDEs", "Category Theory", "Classical Analysis and ODEs", "Combinatorics", "Commutative Algebra", "Complex Variables", "Differential Geometry", "Dynamical Systems", "Functional Analysis", "General Mathematics", "General Topology", "Geometric Topology", "Group Theory", "History and Overview", "Information Theory", "K-Theory and Homology", "Logic", "Mathematical Physics", "Metric Geometry", "Number Theory", "Numerical Analysis", "Operator Algebras", "Optimization and Control", "Probability", "Quantum Algebra", "Representation Theory", "Rings and Algebras", "Spectral Theory", "Statistics Theory", "Symplectic Geometry"],
    "Computer Science": ["Artificial Intelligence", "Computation and Language", "Computational Complexity", "Computational Engineering, Finance, and Science", "Computational Geometry", "Computer Science and Game Theory", "Computer Vision and Pattern Recognition", "Computers and Society", "Cryptography and Security", "Data Structures and Algorithms", "Databases", "Digital Libraries", "Discrete Mathematics", "Distributed, Parallel, and Cluster Computing", "Emerging Technologies", "Formal Languages and Automata Theory", "General Literature", "Graphics", "Hardware Architecture", "Human-Computer Interaction", "Information Retrieval", "Information Theory", "Logic in Computer Science", "Machine Learning", "Mathematical Software", "Multiagent Systems", "Multimedia", "Networking and Internet Architecture", "Neural and Evolutionary Computing", "Numerical Analysis", "Operating Systems", "Other Computer Science", "Performance", "Programming Languages", "Robotics", "Social and Information Networks", "Software Engineering", "Sound", "Symbolic Computation", "Systems and Control"],
    "Quantitative Biology": ["Biomolecules", "Cell Behavior", "Genomics", "Molecular Networks", "Neurons and Cognition", "Other Quantitative Biology", "Populations and Evolution", "Quantitative Methods", "Subcellular Processes", "Tissues and Organs"],
    "Quantitative Finance": ["Computational Finance", "Economics", "General Finance", "Mathematical Finance", "Portfolio Management", "Pricing of Securities", "Risk Management", "Statistical Finance", "Trading and Market Microstructure"],
    "Statistics": ["Applications", "Computation", "Machine Learning", "Methodology", "Other Statistics", "Statistics Theory"],
    "Electrical Engineering and Systems Science": ["Audio and Speech Processing", "Image and Video Processing", "Signal Processing", "Systems and Control"],
    "Economics": ["Econometrics", "General Economics", "Theoretical Economics"]
}


def subscribe(email, subject, physics_subject, subsubjects, interest):
    if subject == "Physics":
        if isinstance(physics_subject, list):
            raise gr.Error("You must choose a physics category.")
        subject = physics_subject
        abbr = physics_categories[subject]
    else:
        abbr = categories[subject]
    if subsubjects and subsubjects != ["None"]:
        return f"Subscribing {email} to {subsubjects} in {subject} ({abbr}), sorting by {interest}"
    else:
        return f"Subscribing {email} to all subsubjects in {subject} ({abbr}), sorting by {interest}"


def test(*args):
    return subscribe(*args)


def sample(email, subject, physics_subject, subsubjects, interest):
    if subject == "Physics":
        if isinstance(physics_subject, list):
            raise gr.Error("You must choose a physics category.")
        subject = physics_subject
        abbr = physics_categories[subject]
    else:
        abbr = categories[subject]
    papers = get_papers(abbr, limit=2)
    return f"Title: {papers[0]['title']}\nTitle: {papers[1]['title']}"


def change_subsubject(subject, physics_subject):
    if subject != "Physics":
        return gr.Dropdown.update(choices=subcategories[subject], value=[], visible=True)
    else:
        print(physics_subject)
        if physics_subject and not isinstance(physics_subject, list):
            print(subcategories[physics_subject])
            return gr.Dropdown.update(choices=subcategories[physics_subject], value=[], visible=True)
        else:
            return gr.Dropdown.update(choices=[], value=[], visible=False)


def change_physics(subject):
    if subject != "Physics":
        return gr.Dropdown.update(visible=False, value=[])
    else:
        return gr.Dropdown.update(physics_categories, visible=True)


with gr.Blocks() as demo:
    with gr.Column():
        email = gr.Textbox(label="Email address")
        subject = gr.Radio(
            list(categories.keys()), label="Topic to subscribe to"
        )
        physics_subject = gr.Dropdown(physics_categories, value=[], multiselect=False, label="Physics category", visible=False, info="")
        subsubject = gr.Dropdown(
                [], value=[], multiselect=True, label="Sub-Subject", info="", visible=False)
        subject.change(fn=change_physics, inputs=[subject], outputs=physics_subject)
        subject.change(fn=change_subsubject, inputs=[subject, physics_subject], outputs=subsubject)
        physics_subject.change(fn=change_subsubject, inputs=[subject, physics_subject], outputs=subsubject)


        interest = gr.Textbox(label="A description of what you are interested in")
    output = gr.Textbox(label="Output Box")
    sample_output = gr.Textbox(label="Sample")
    subscribe_btn = gr.Button("Subscribe")
    test_btn = gr.Button("Send test email")
    subscribe_btn.click(fn=subscribe, inputs=[email, subject, physics_subject, subsubject, interest], outputs=output, api_name="subscribe")
    test_btn.click(fn=test, inputs=[email, subject, physics_subject, subsubject, interest], outputs=output, api_name="subscribe")
    subject.change(fn=sample, inputs=[email, subject, physics_subject, subsubject, interest], outputs=sample_output)
    physics_subject.change(fn=sample, inputs=[email, subject, physics_subject, subsubject, interest], outputs=sample_output)
    subsubject.change(fn=sample, inputs=[email, subject, physics_subject, subsubject, interest], outputs=sample_output)
    interest.change(fn=sample, inputs=[email, subject, physics_subject, subsubject, interest], outputs=sample_output)

demo.launch()
