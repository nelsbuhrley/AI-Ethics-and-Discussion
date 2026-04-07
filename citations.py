"""
Citation processor for formatting in-text citations and generating bibliography.

Usage in markdown:
  |src|'source_id'|'short'|  -> Author (Year)
  |src|'source_id'|'long'|   -> Full formatted citation
"""

import re
import yaml
from typing import Dict, List, Tuple
from pathlib import Path


class CitationManager:
    """Manages citations from YAML source and formats them according to style."""
    
    def __init__(self, sources_path: str = "sources.yaml"):
        """Initialize citation manager with sources file."""
        self.sources_path = Path(sources_path)
        self.sources = {}
        self.citations_used = {}  # Track which citations are used in content
        self._load_sources()
    
    def _load_sources(self):
        """Load sources from YAML file."""
        if self.sources_path.exists():
            with open(self.sources_path, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'sources' in data:
                    for source in data['sources']:
                        self.sources[source['id']] = source
    
    def format_short(self, source_id: str) -> str:
        """
        Format short citation: Author (Year)
        
        Args:
            source_id: Identifier of the source
            
        Returns:
            Formatted short citation string
        """
        if source_id not in self.sources:
            return f"[Citation not found: {source_id}]"
        
        source = self.sources[source_id]
        author = source.get('author', 'Unknown')
        year = source.get('year', 'n.d.')
        return f"{author} ({year})"
    
    def format_long(self, source_id: str) -> str:
        """
        Format long citation: Full formatted entry.
        
        Args:
            source_id: Identifier of the source
            
        Returns:
            Formatted long citation string
        """
        if source_id not in self.sources:
            return f"[Citation not found: {source_id}]"
        
        source = self.sources[source_id]
        
        # Build citation based on source type
        author = source.get('author', 'Unknown')
        year = source.get('year', 'n.d.')
        title = source.get('title', 'Untitled')
        source_type = source.get('type', 'web')
        publisher = source.get('publisher', '')
        url = source.get('url', '')
        
        # Web-friendly, clean format
        citation = f"{author} ({year}). {title}"
        
        if publisher:
            citation += f". {publisher}"
        
        if url:
            citation += f". Retrieved from {url}"
        
        return citation
    
    def process_content(self, content: str) -> Tuple[str, List[str]]:
        """
        Process markdown content and replace citation syntax with formatted citations.
        
        Pattern: |src|'source_id'|'short_or_long'|
        
        Args:
            content: Markdown content with citation markers
            
        Returns:
            Tuple of (processed_content, list_of_used_source_ids)
        """
        # Pattern to match |src|'id'|'format'|
        pattern = r"\|src\|'([^']+)'\|'(short|long)'\|"
        
        used_sources = []
        
        def replace_citation(match):
            source_id = match.group(1)
            format_type = match.group(2)
            
            # Track this source
            if source_id not in used_sources:
                used_sources.append(source_id)
            
            # Format appropriately
            if format_type == 'short':
                return self.format_short(source_id)
            else:  # long
                return self.format_long(source_id)
        
        processed = re.sub(pattern, replace_citation, content)
        return processed, used_sources
    
    def generate_bibliography(self, source_ids: List[str] = None) -> str:
        """
        Generate formatted bibliography section (HTML).
        
        Args:
            source_ids: List of source IDs to include. If None, includes all used sources.
                       If empty list, includes all sources.
        
        Returns:
            HTML-formatted bibliography
        """
        # Determine which sources to include
        if source_ids is None:
            # Default: show all sources
            sources_to_show = list(self.sources.values())
        elif len(source_ids) == 0:
            sources_to_show = list(self.sources.values())
        else:
            sources_to_show = [self.sources[sid] for sid in source_ids if sid in self.sources]
        
        # Sort alphabetically by author
        sources_to_show.sort(key=lambda s: s.get('author', 'Unknown').lower())
        
        html = '<div class="citations">\n'
        html += '<h2>Sources</h2>\n'
        html += '<dl class="bibliography">\n'
        
        for source in sources_to_show:
            source_id = source['id']
            author = source.get('author', 'Unknown')
            year = source.get('year', 'n.d.')
            
            # Use short format as the key, long as description
            short = self.format_short(source_id)
            long = self.format_long(source_id)
            
            html += f'  <dt id="cite-{source_id}" class="citation-entry">{short}</dt>\n'
            html += f'  <dd>{long}</dd>\n'
        
        html += '</dl>\n'
        html += '</div>\n'
        
        return html


def process_all_markdown_files(content_dir: str = "content", 
                               sources_path: str = "sources.yaml",
                               output_citations_file: str = "citations.html") -> None:
    """
    Process all markdown files in directory, extract citations, and generate bibliography.
    
    Args:
        content_dir: Directory containing markdown files
        sources_path: Path to sources YAML file
        output_citations_file: Where to save generated citations HTML
    """
    manager = CitationManager(sources_path)
    
    all_citations = set()
    content_path = Path(content_dir)
    
    # Walk through all markdown files
    for md_file in content_path.rglob("*.md"):
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Extract citations but don't replace yet (just for collecting)
        pattern = r"\|src\|'([^']+)'\|'(short|long)'\|"
        matches = re.findall(pattern, content)
        for source_id, _ in matches:
            all_citations.add(source_id)
    
    # Generate bibliography with found citations
    bibliography = manager.generate_bibliography(list(all_citations))
    
    # Save to file
    with open(output_citations_file, 'w') as f:
        f.write(bibliography)
    
    print(f"Bibliography saved to {output_citations_file}")
    print(f"Found {len(all_citations)} citations in use")


if __name__ == "__main__":
    # Example usage
    manager = CitationManager()
    
    # Example content
    test_content = """
    This is an important finding |src|'source_1'|'short'|.
    
    As detailed in research |src|'source_1'|'long'|, the implications are significant.
    """
    
    processed, used = manager.process_content(test_content)
    print("Processed content:")
    print(processed)
    print(f"\nSources used: {used}")
    print("\nGenerated bibliography:")
    print(manager.generate_bibliography(used))
