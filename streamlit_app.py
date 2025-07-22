import streamlit as st

# Import libraries
import pandas as pd
import time
import urllib
import urllib.request
import requests
import xml.etree.ElementTree as etree
# import pyperclip  

# Heading
st.title("Scholar Search")
st.write("Streamlining the discovery of emerging research talent by analyzing recent publications and their authors")

with st.expander("How It Works"):
    st.markdown("""
    ##### Using the Tool:
    Configure Search Parameters:
    - Select arXiv research category
    - Set publication date range
    - Adjust author metrics thresholds
    - Add optional keywords to target specific research areas
    
    ##### Understanding Results:
    Each result card shows:
    - Author name and their recent arXiv publication (full paper on arXiv is linked)
    - Academic metrics (citations, h-index) from Semantic Scholar
    - Institutional affiliations when available
    - Research impact insights
    - Author profile links on Semantic Scholar (*Note: author profiles are not always accurate and should be manually verified before outreach*)
    
    ##### Key Features:
    - **Quality Filters:** Authors must have minimum 10 publications and 100 citations
    - **Intelligent Ranking:** Results are ordered by h-index (highest to lowest), with citation count as a secondary sort for ties
    - **Data Export:** Download results as CSV for systematic candidate tracking
    """)

# Input forms
with st.form("search_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        
        # Complete list of ArXiv categories
        category_options = {
            'cs.AI': 'Artificial Intelligence',
            'cs.AR': 'Hardware Architecture',
            'cs.CC': 'Computational Complexity',
            'cs.CE': 'Computational Engineering',
            'cs.CG': 'Computational Geometry',
            'cs.CL': 'Computation and Language',
            'cs.CR': 'Cryptography and Security',
            'cs.CV': 'Computer Vision and Pattern Recognition',
            'cs.CY': 'Computers and Society',
            'cs.DB': 'Databases',
            'cs.DC': 'Distributed Computing',
            'cs.DL': 'Digital Libraries',
            'cs.DM': 'Discrete Mathematics',
            'cs.DS': 'Data Structures and Algorithms',
            'cs.ET': 'Emerging Technologies',
            'cs.FL': 'Formal Languages and Automata Theory',
            'cs.GL': 'General Literature',
            'cs.GR': 'Graphics',
            'cs.GT': 'Computer Science and Game Theory',
            'cs.HC': 'Human-Computer Interaction',
            'cs.IR': 'Information Retrieval',
            'cs.IT': 'Information Theory',
            'cs.LG': 'Machine Learning',
            'cs.LO': 'Logic in Computer Science',
            'cs.MA': 'Multiagent Systems',
            'cs.MM': 'Multimedia',
            'cs.MS': 'Mathematical Software',
            'cs.NA': 'Numerical Analysis',
            'cs.NE': 'Neural and Evolutionary Computing',
            'cs.NI': 'Networking and Internet Architecture',
            'cs.OH': 'Other Computer Science',
            'cs.OS': 'Operating Systems',
            'cs.PF': 'Performance',
            'cs.PL': 'Programming Languages',
            'cs.RO': 'Robotics',
            'cs.SC': 'Symbolic Computation',
            'cs.SD': 'Sound',
            'cs.SE': 'Software Engineering',
            'cs.SI': 'Social and Information Networks',
            'cs.SY': 'Systems and Control',
            'stat.AP': 'Applications',
            'stat.CO': 'Computation',
            'stat.ML': 'Machine Learning',
            'stat.ME': 'Methodology',
            'stat.OT': 'Other Statistics',
            'stat.TH': 'Theory'
        }

        selected_cats = st.multiselect("Select 1 or More [Research Categories](https://arxiv.org/category_taxonomy)", options=category_options.keys(), format_func=lambda x: f"{x} - {category_options[x]}")
        if not selected_cats:
            st.warning("Please select at least one category")
        
        # category_selection = st.selectbox("[ArXiv Category](https://arxiv.org/category_taxonomy)", options=category_options)
        # # Extract category code from selection (everything before the dash)
        # category = category_selection.split(" - ")[0].strip()    
        
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
        'limit': 5
    }
    try:
        time.sleep(0.1)
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['data'] and len(data['data']) > 0:
                # If there are multiple authors with the same name, choose the one with papers in CS and then with the most citations)
                cs_authors = []
                for author in data['data']:
                    if author.get('papers'):
                        for paper in author['papers']:
                            if paper.get('fieldsOfStudy') and 'Computer Science' in paper['fieldsOfStudy']:
                                cs_authors.append(author)
                                break
                # If we found CS authors, return the one with highest citations
                if cs_authors:
                    best_author = max(cs_authors, key=lambda x: x.get('citationCount', 0) or 0)
                else:
                    # If no CS authors found, just take the highest cited author
                    best_author = max(data['data'], key=lambda x: x.get('citationCount', 0) or 0)
                
                return {
                    'name': best_author.get('name'),
                    'paper_count': best_author.get('paperCount'),
                    'citation_count': best_author.get('citationCount'),
                    'h_index': best_author.get('hIndex'),
                    'affiliation': best_author.get('affiliations', []),
                    'url': best_author.get('url')
                }
        else:
            return None

    except Exception as e:
        print(e)
        return None
    pass

# Get results:
def get_results(categories, start_date, end_date, num_results, author_limit, max_h_index=25, keywords=[]):
    cat_query = '%OR%'.join([f"cat:{cat}" for cat in categories]) # NEW FOR CHECKBOX IMPLEMENTATION
    url = f"http://export.arxiv.org/api/query?search_query=cat:{cat_query}+AND+submittedDate:[{start_date}0000+TO+{end_date}2359]&start=0&max_results={num_results}&sortBy=submittedDate&sortOrder=descending"
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
if submit_button and selected_cats:
    try:
        with st.spinner('Fetching results...'):
            # Format dates
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            # Process keywords
            keyword_list = [k.strip() for k in keywords.split(',')] if keywords else []

            # Get results
            results = get_results(
                categories=selected_cats,
                start_date=start_date_str,
                end_date=end_date_str,
                num_results=num_results,
                author_limit=author_limit,
                max_h_index=max_h_index,
                keywords=keyword_list
            )
            
            # Display results
            if not results.empty:
                # Create two columns for the header area
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.success(f"Found {len(results)} matching authors")
                with col2:
                    # Add download button next to the success message
                    csv = results.to_csv(index=False)
                    st.download_button(
                        label="Download results to a CSV file",
                        data=csv,
                        file_name="arxiv_sourcing_results.csv",
                        mime="text/csv"
                    )

                # New author results:
                st.markdown("""
                    <style>
                    .author-card {
                        padding: 20px;
                        border-radius: 5px;
                        background-color: #f0f2f6;
                        margin-bottom: 10px;
                    }
                    .links {
                        margin-top: 10px;
                        padding-top: 10px;
                        border-top: 1px solid #e0e0e0;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                
                for idx, row in results.iterrows():
                    with st.container():
                        arxiv_id = row['id'].split('/')[-1]
                        arxiv_link = f"https://arxiv.org/abs/{arxiv_id}"
                        st.markdown(f"""
                        <div class="author-card">
                        <h3>{row['authors']}</h3>
                        <p><b>Paper:</b> <a href="{arxiv_link}">{row['title']}</a></p>
                        <p><b>Citations:</b> {row['citation_count']} | <b>H-index:</b> {row['h_index']}</p>
                        <p><b>Affiliation:</b> {row['affiliations']}</p>
                        <p>{row['insights']}</p>""" + 
                        (f"""<div class="links">
                        <p><a href='{row['profile_url']}'>View <i>Potential</i> Semantic Scholar Profile</a></p>
                        </div>""" if row['profile_url'] else "") +
                        """</div>
                        """, unsafe_allow_html=True)        

                        
                # Create expandable sections for each author
                # for idx, row in results.iterrows():
                #     with st.expander(f"{row['authors']} (h-index: {row['h_index']})"):
                #         arxiv_id = row['id'].split('/')[-1]  # Extract ID from the full URL
                #         arxiv_link = f"https://arxiv.org/abs/{arxiv_id}"
                        
                #         st.write(f"**Paper Title:** [{row['title']}]({arxiv_link})")
                #         st.write(f"**Citations:** {row['citation_count']}")
                #         st.write(f"**Total Papers:** {row['paper_count']}")
                #         st.write(f"**Affiliations:** {row['affiliations']}")
                #         st.write(f"**Insights:** {row['insights']}")
                #         if row['profile_url']:
                #             st.write(f"[View *Potential* Semantic Scholar Profile]({row['profile_url']})")
                
            else:
                st.warning("No results found matching your criteria.")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
