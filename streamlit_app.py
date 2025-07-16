import streamlit as st

# Import libraries
import pandas as pd
import time
import urllib
import urllib.request
import requests
import xml.etree.ElementTree as etree

# Heading
st.title("Research Paper Sourcing Explorer")
st.write("This app analyzes authors from recent ArXiv papers using Semantic Scholar data")

# Input forms
with st.form("search_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("[ArXiv Category](https://arxiv.org/category_taxonomy)")
        # Complete list of ArXiv categories
        category_options = [
            # Computer Science
            "cs.AI - Artificial Intelligence",
            "cs.AR - Hardware Architecture",
            "cs.CC - Computational Complexity",
            "cs.CE - Computational Engineering",
            "cs.CG - Computational Geometry",
            "cs.CL - Computation and Language",
            "cs.CR - Cryptography and Security",
            "cs.CV - Computer Vision and Pattern Recognition",
            "cs.CY - Computers and Society",
            "cs.DB - Databases",
            "cs.DC - Distributed Computing",
            "cs.DL - Digital Libraries",
            "cs.DM - Discrete Mathematics",
            "cs.DS - Data Structures and Algorithms",
            "cs.ET - Emerging Technologies",
            "cs.FL - Formal Languages and Automata Theory",
            "cs.GL - General Literature",
            "cs.GR - Graphics",
            "cs.GT - Computer Science and Game Theory",
            "cs.HC - Human-Computer Interaction",
            "cs.IR - Information Retrieval",
            "cs.IT - Information Theory",
            "cs.LG - Machine Learning",
            "cs.LO - Logic in Computer Science",
            "cs.MA - Multiagent Systems",
            "cs.MM - Multimedia",
            "cs.MS - Mathematical Software",
            "cs.NA - Numerical Analysis",
            "cs.NE - Neural and Evolutionary Computing",
            "cs.NI - Networking and Internet Architecture",
            "cs.OH - Other Computer Science",
            "cs.OS - Operating Systems",
            "cs.PF - Performance",
            "cs.PL - Programming Languages",
            "cs.RO - Robotics",
            "cs.SC - Symbolic Computation",
            "cs.SD - Sound",
            "cs.SE - Software Engineering",
            "cs.SI - Social and Information Networks",
            "cs.SY - Systems and Control",
            
            # Physics
            "physics.acc-ph - Accelerator Physics",
            "physics.app-ph - Applied Physics",
            "physics.ao-ph - Atmospheric and Oceanic Physics",
            "physics.atom-ph - Atomic Physics",
            "physics.bio-ph - Biological Physics",
            "physics.chem-ph - Chemical Physics",
            "physics.class-ph - Classical Physics",
            "physics.comp-ph - Computational Physics",
            "physics.data-an - Data Analysis, Statistics and Probability",
            "physics.flu-dyn - Fluid Dynamics",
            "physics.gen-ph - General Physics",
            "physics.geo-ph - Geophysics",
            "physics.hist-ph - History and Philosophy of Physics",
            "physics.ins-det - Instrumentation and Detectors",
            "physics.med-ph - Medical Physics",
            "physics.optics - Optics",
            "physics.ed-ph - Physics Education",
            "physics.soc-ph - Physics and Society",
            "physics.plasm-ph - Plasma Physics",
            "physics.pop-ph - Popular Physics",
            "physics.space-ph - Space Physics",
            
            # Mathematics
            "math.AG - Algebraic Geometry",
            "math.AT - Algebraic Topology",
            "math.AP - Analysis of PDEs",
            "math.CT - Category Theory",
            "math.CA - Classical Analysis and ODEs",
            "math.CO - Combinatorics",
            "math.AC - Commutative Algebra",
            "math.CV - Complex Variables",
            "math.DG - Differential Geometry",
            "math.DS - Dynamical Systems",
            "math.FA - Functional Analysis",
            "math.GM - General Mathematics",
            "math.GN - General Topology",
            "math.GT - Geometric Topology",
            "math.GR - Group Theory",
            "math.HO - History and Overview",
            "math.IT - Information Theory",
            "math.KT - K-Theory and Homology",
            "math.LO - Logic",
            "math.MP - Mathematical Physics",
            "math.MG - Metric Geometry",
            "math.NT - Number Theory",
            "math.NA - Numerical Analysis",
            "math.OA - Operator Algebras",
            "math.OC - Optimization and Control",
            "math.PR - Probability",
            "math.QA - Quantum Algebra",
            "math.RT - Representation Theory",
            "math.RA - Rings and Algebras",
            "math.SP - Spectral Theory",
            "math.ST - Statistics Theory",
            "math.SG - Symplectic Geometry",
            
            # Statistics
            "stat.AP - Applications",
            "stat.CO - Computation",
            "stat.ML - Machine Learning",
            "stat.ME - Methodology",
            "stat.OT - Other Statistics",
            "stat.TH - Theory"
        ]
        
        category_selection = st.selectbox(
            "",
            options=category_options,
            help="Select an ArXiv category"
        )
        
        # Extract category code from selection (everything before the dash)
        category = category_selection.split(" - ")[0].strip()    
        
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        
    with col2:
        num_results = st.number_input("Number of Results", min_value=1, max_value=100, value=10)
        author_limit = st.number_input("Author Limit per Paper", min_value=1, value=5)
        max_h_index = st.number_input("Maximum H-Index", min_value=1, value=25)
    
    keywords = st.text_input("Keywords (comma-separated)")
    submit_button = st.form_submit_button("Search")

# Helper function
# This helper function takes an author's name and returns key information about them
def get_author_info(author_name):
    base_url = "http://api.semanticscholar.org/graph/v1/author/search"
    params = {
        'query': author_name, # Note that I am searching by author name instead of paper name because new papers on arXiv are not yet on semantic scholar (delayed entry)
        'fields': 'name,paperCount,citationCount,hIndex,affiliations,url',
    }
    try:
        time.sleep(1)
        response = requests.get(base_url, params=params) #, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data['data'] and len(data['data']) > 0:
                # If there are multiple authors with the same name, choose the one with the most citations (the reason for this is that if there are multiple authors with the same name, let's find the best one and manually fix it if it's wrong. If we didn't find the best one, we may filter it out and miss a great candidate).
                most_cited_author = max(data['data'], key=lambda x: x.get('citationCount', 0) or 0)
                return {
                    'name': most_cited_author.get('name'),
                    'paper_count': most_cited_author.get('paperCount'),
                    'citation_count': most_cited_author.get('citationCount'),
                    'h_index': most_cited_author.get('hIndex'),
                    'affiliation': most_cited_author.get('affiliations', []),
                    'url': most_cited_author.get('url')
                }
        else:
            return None

    except Exception as e:
        print(e)
        return None

    pass

# Get results:
def get_results(category, start_date, end_date, num_results, author_limit, max_h_index=25, keywords=[]):
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}+AND+submittedDate:[{start_date}0000+TO+{end_date}2359]&start=0&max_results={num_results}&sortBy=submittedDate&sortOrder=descending"
    response = urllib.request.urlopen(url).read()

    root = etree.fromstring(response)
    data = []
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}

    for entry in root.findall('atom:entry', namespace):
        authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
        limited_authors = authors[:author_limit]

        paper = {
            'authors': limited_authors,
            'id': entry.find('atom:id', namespace).text,
            'title': entry.find('atom:title', namespace).text.strip(),
            'summary': entry.find('atom:summary', namespace).text.strip(),
            'published': entry.find('atom:published', namespace).text.strip(),
        }
        data.append(paper)

    df = pd.DataFrame(data)

    # FILTER FOR KEYWORDS if there is a keyword input
    if keywords != []:
        mask = df['summary'].str.contains(keywords[0], case=False, na=False)
        for word in keywords[1:]:
            mask = mask & df['summary'].str.contains(word, case=False, na=False)
        df = df[mask].reset_index(drop=True)


    df = df.explode('authors')  # Make each row an author
    author_data = []

    for author in df['authors'].unique():
        info = get_author_info(author)
        if info != None:
            new_info = {
                'authors': author,
                'semantic_scholar_name': info['name'],
                'paper_count': info['paper_count'],
                'citation_count': info['citation_count'],
                'h_index': info['h_index'],
                'affiliations': ', '.join(info['affiliation']) if info['affiliation'] else None,
                'profile_url': info['url']
            }
            author_data.append(new_info)

    author_df = pd.DataFrame(author_data)
    merged_df = df.merge(author_df, on='authors')
    filtered_df = merged_df[(merged_df['paper_count'] >= 10) & (merged_df['citation_count'] >= 100)].reset_index(
        drop=True)  # Per Jayesh's recommendation, filter out authors without at least 10 publications and 100 citations
    filtered_df_2 = filtered_df[filtered_df['h_index'] <= max_h_index].reset_index(
        drop=True)  # Per Ben's recommendation, filter out authors with an h-index greater than 25. UPDATE: user customizes their max h index based on role looking to fill. Default is 25 if there is no input
    sorted_df = filtered_df_2.sort_values(by=['h_index', 'citation_count'], ascending=[False, False]).reset_index(
        drop=True)  # sorts by h_index first, then citation_count for ties

    # Generate insights about each author
    insights = []
    for index, row in sorted_df.iterrows():
        author_notes = []
        if row['citation_count'] > merged_df['citation_count'].mean():
            author_notes.append(f"Above-average citation impact with {row['citation_count']} citations")
        if row['h_index'] > merged_df['h_index'].median():
            author_notes.append(f"Strong h-index of {row['h_index']}")
        if row['paper_count'] > merged_df['paper_count'].mean():
            author_notes.append(f"Productive researcher with {row['paper_count']} publications")
        insights.append(" | ".join(author_notes))
    sorted_df['insights'] = insights

    result = sorted_df[['authors', 'id', 'title', 'paper_count', 'citation_count', 'h_index', 'insights', 'affiliations', 'profile_url']]

    return result

    pass

# Handle form submission
if submit_button:
    try: 
        with st.spinner("Fetching results..."):
            # Format dates
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            # Process keywords
            keyword_list = [k.strip() for k in keywords.split(',')] if keywords else []
            
            # Get results
            results = get_results(
                category=category,
                start_date=start_date_str,
                end_date=end_date_str,
                num_results=num_results,
                author_limit=author_limit,
                max_h_index=max_h_index,
                keywords=keyword_list
            )
            
            # Display results
            if not results.empty:
                st.success(f"Found {len(results)} matching authors")
                
                # Create expandable sections for each author
                for idx, row in results.iterrows():
                    with st.expander(f"{row['authors']} (h-index: {row['h_index']})"):
                        st.write(f"**Paper Title:** {row['title']}")
                        st.write(f"**Citations:** {row['citation_count']}")
                        st.write(f"**Total Papers:** {row['paper_count']}")
                        st.write(f"**Affiliations:** {row['affiliations']}")
                        st.write(f"**Insights:** {row['insights']}")
                        if row['profile_url']:
                            st.write(f"[View Semantic Scholar Profile]({row['profile_url']})")
                
                # Add download button
                csv = results.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="author_results.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No results found matching your criteria.")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
