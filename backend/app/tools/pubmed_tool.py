"""
RetinAI Backend — PubMed E-utilities API Wrapper
Searches PubMed database for scientific literature on Diabetic Retinopathy.
"""
import os
import requests
from typing import List, Dict, Any

# Optional PubMed email registration to prevent rate limiting
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "your.email@example.com")


def search_pubmed(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search PubMed for articles and return structured citation information.
    
    Args:
        query: Search term (e.g. "diabetic retinopathy moderate stage management")
        max_results: Maximum number of papers to fetch
        
    Returns:
        List of dictionaries containing title, authors, journal, year, and url.
    """
    try:
        # 1. Search PubMed to get PMIDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "tool": "RetinAI",
            "email": PUBMED_EMAIL
        }
        
        search_res = requests.get(search_url, params=search_params, timeout=10)
        search_res.raise_for_status()
        search_data = search_res.json()
        
        pmids = search_data.get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return []
            
        # 2. Fetch summaries for the PMIDs
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
            "tool": "RetinAI",
            "email": PUBMED_EMAIL
        }
        
        summary_res = requests.get(summary_url, params=summary_params, timeout=10)
        summary_res.raise_for_status()
        summary_data = summary_res.json()
        
        results = []
        result_details = summary_data.get("result", {})
        
        for pmid in pmids:
            paper_info = result_details.get(pmid)
            if not paper_info:
                continue
                
            title = paper_info.get("title", "Untitled Article")
            journal = paper_info.get("source", "Unknown Journal")
            pubdate = paper_info.get("pubdate", "")
            
            # Format author list: "Author1, Author2, et al."
            authors_list = paper_info.get("authors", [])
            if len(authors_list) == 0:
                authors = "Unknown Authors"
            elif len(authors_list) == 1:
                authors = authors_list[0].get("name", "Unknown")
            else:
                authors = f"{authors_list[0].get('name', 'Unknown')}, et al."
                
            # Extract year from pubdate
            year = pubdate.split(" ")[0] if pubdate else "N/A"
            # Clean title formatting
            if title.endswith("."):
                title = title[:-1]
                
            results.append({
                "pmid": pmid,
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })
            
        return results
        
    except Exception as e:
        print(f"[PubMed Tool Error] {e}")
        return []


if __name__ == "__main__":
    # Test query
    print("Testing PubMed search...")
    res = search_pubmed("diabetic retinopathy stage 2 moderate", max_results=2)
    for i, paper in enumerate(res):
        print(f"\n[{i+1}] {paper['title']}")
        print(f"    Authors: {paper['authors']}")
        print(f"    Source : {paper['journal']} ({paper['year']})")
        print(f"    Link   : {paper['url']}")
