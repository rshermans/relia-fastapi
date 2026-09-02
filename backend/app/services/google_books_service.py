"""
Serviço de Busca e Consulta de Metadados via Google Books API
Permite pesquisar obras literárias, resumos, autores e links de domínio público.
"""

import httpx
from typing import List, Dict, Any

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

class GoogleBooksService:
    async def search_volumes(self, query: str, lang_restrict: str = "pt") -> List[Dict[str, Any]]:
        params = {
            "q": query,
            "langRestrict": lang_restrict,
            "maxResults": 10,
            "orderBy": "relevance"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(GOOGLE_BOOKS_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for item in data.get("items", []):
                    vol_info = item.get("volumeInfo", {})
                    access_info = item.get("accessInfo", {})
                    
                    results.append({
                        "google_book_id": item.get("id"),
                        "title": vol_info.get("title"),
                        "subtitle": vol_info.get("subtitle"),
                        "authors": vol_info.get("authors", []),
                        "publisher": vol_info.get("publisher"),
                        "published_date": vol_info.get("publishedDate"),
                        "description": vol_info.get("description"),
                        "categories": vol_info.get("categories", []),
                        "page_count": vol_info.get("pageCount"),
                        "thumbnail": vol_info.get("imageLinks", {}).get("thumbnail"),
                        "preview_link": vol_info.get("previewLink"),
                        "info_link": vol_info.get("infoLink"),
                        "is_public_domain": access_info.get("publicDomain", False),
                        "epub_available": access_info.get("epub", {}).get("isAvailable", False),
                        "pdf_available": access_info.get("pdf", {}).get("isAvailable", False),
                    })
                return results
            except Exception as e:
                print(f"[GoogleBooksService] Erro: {e}")
                return []

google_books_service = GoogleBooksService()
