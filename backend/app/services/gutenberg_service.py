"""
Serviço de Integração com o Project Gutenberg (via Gutendex API)
Permite pesquisa por autor, título, assunto e download do texto integral com sanitização automática.
"""

import httpx
from typing import List, Dict, Any, Optional
from backend.app.services.text_sanitizer import text_sanitizer

GUTENDEX_API_URL = "https://gutendex.com/books"

class GutenbergService:
    async def search_books(self, query: str, languages: str = "pt") -> List[Dict[str, Any]]:
        """
        Pesquisa obras no Project Gutenberg filtrando por termo e idioma (padrão 'pt').
        """
        params = {
            "search": query,
            "languages": languages
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(GUTENDEX_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for item in data.get("results", []):
                    # Localizar URLs de texto ou epub
                    formats = item.get("formats", {})
                    txt_url = (
                        formats.get("text/plain; charset=utf-8") or 
                        formats.get("text/plain; charset=us-ascii") or 
                        formats.get("text/plain")
                    )
                    epub_url = formats.get("application/epub+zip")
                    cover_url = formats.get("image/jpeg")
                    
                    authors = [a.get("name", "Desconhecido") for a in item.get("authors", [])]
                    
                    results.append({
                        "gutenberg_id": item.get("id"),
                        "title": item.get("title"),
                        "authors": authors,
                        "subjects": item.get("subjects", []),
                        "languages": item.get("languages", []),
                        "download_count": item.get("download_count", 0),
                        "txt_url": txt_url,
                        "epub_url": epub_url,
                        "cover_url": cover_url
                    })
                return results
            except Exception as e:
                print(f"[GutenbergService] Erro na busca: {e}")
                # Retorna lista de sugestões canónicas do corpus IAVE se a API estiver offline
                return self._get_canonical_fallback_suggestions(query)

    async def fetch_full_text(self, txt_url: str, is_verse: bool = False) -> Dict[str, Any]:
        """
        Descarrega e limpa o texto integral a partir do link do Gutenberg.
        """
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(txt_url)
            resp.raise_for_status()
            raw_text = resp.text
            
            cleaned_text, stats = text_sanitizer.normalize_literary_text(raw_text, is_verse=is_verse)
            return {
                "cleaned_text": cleaned_text,
                "stats": stats,
                "raw_length": len(raw_text)
            }

    def _get_canonical_fallback_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Sugestões canónicas de obras de domínio público do programa IAVE."""
        corpus = [
            {
                "gutenberg_id": 3333,
                "title": "Os Lusíadas",
                "authors": ["Camões, Luís de"],
                "subjects": ["Epic poetry, Portuguese", "Explorers -- Portugal -- Poetry"],
                "languages": ["pt"],
                "download_count": 1500,
                "txt_url": "https://www.gutenberg.org/cache/epub/3333/pg3333.txt",
                "epub_url": "https://www.gutenberg.org/ebooks/3333.epub.noimages",
                "cover_url": "https://www.gutenberg.org/cache/epub/3333/pg3333.cover.medium.jpg"
            },
            {
                "gutenberg_id": 14781,
                "title": "Sermão de Santo António aos Peixes",
                "authors": ["Vieira, António"],
                "subjects": ["Sermons, Portuguese -- 17th century", "Satire, Portuguese"],
                "languages": ["pt"],
                "download_count": 980,
                "txt_url": "https://www.gutenberg.org/cache/epub/14781/pg14781.txt",
                "epub_url": "https://www.gutenberg.org/ebooks/14781.epub.noimages",
                "cover_url": "https://www.gutenberg.org/cache/epub/14781/pg14781.cover.medium.jpg"
            },
            {
                "gutenberg_id": 23555,
                "title": "Auto da Barca do Inferno",
                "authors": ["Vicente, Gil"],
                "subjects": ["Portuguese drama -- 16th century"],
                "languages": ["pt"],
                "download_count": 1200,
                "txt_url": "https://www.gutenberg.org/cache/epub/23555/pg23555.txt",
                "epub_url": "https://www.gutenberg.org/ebooks/23555.epub.noimages",
                "cover_url": "https://www.gutenberg.org/cache/epub/23555/pg23555.cover.medium.jpg"
            },
            {
                "gutenberg_id": 31552,
                "title": "Os Maias",
                "authors": ["Queirós, Eça de"],
                "subjects": ["Portuguese fiction -- 19th century", "Lisbon (Portugal) -- Fiction"],
                "languages": ["pt"],
                "download_count": 2100,
                "txt_url": "https://www.gutenberg.org/cache/epub/31552/pg31552.txt",
                "epub_url": "https://www.gutenberg.org/ebooks/31552.epub.noimages",
                "cover_url": "https://www.gutenberg.org/cache/epub/31552/pg31552.cover.medium.jpg"
            }
        ]
        q = query.lower()
        return [b for b in corpus if q in b["title"].lower() or any(q in a.lower() for a in b["authors"])] or corpus

gutenberg_service = GutenbergService()
