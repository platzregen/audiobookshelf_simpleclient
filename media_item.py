from typing import List, Optional


class Metadata:
    def __init__(self, title: str, title_ignore_prefix: Optional[str] = None,
                 subtitle: Optional[str] = None, author_name: str = '',
                 author_name_lf: Optional[str] = None, narrator_name: Optional[str] = None,
                 series_name: Optional[str] = None, genres: Optional[List[str]] = None,
                 published_year: Optional[int] = None, published_date: Optional[str] = None,
                 publisher: Optional[str] = None, description: Optional[str] = None,
                 isbn: Optional[str] = None, asin: Optional[str] = None,
                 language: Optional[str] = None, explicit: bool = False,
                 abridged: bool = False) -> None:
        self.title = title
        self.title_ignore_prefix = title_ignore_prefix
        self.subtitle = subtitle
        self.author_name = author_name
        self.author_name_lf = author_name_lf
        self.narrator_name = narrator_name
        self.series_name = series_name
        self.genres = genres or []
        self.published_year = published_year
        self.published_date = published_date
        self.publisher = publisher
        self.description = description
        self.isbn = isbn
        self.asin = asin
        self.language = language
        self.explicit = explicit
        self.abridged = abridged


class Media:
    def __init__(self, media_dict):
        self.id = media_dict.get('id')
        self.metadata = media_dict.get('metadata')
        self.cover_path = media_dict.get('coverPath')
        self.tags = media_dict.get('tags')
        self.num_tracks = media_dict.get('numTracks')
        self.num_audio_files = media_dict.get('numAudioFiles')
        self.num_chapters = media_dict.get('numChapters')
        self.num_missing_parts = media_dict.get('numMissingParts')
        self.num_invalid_audio_files = media_dict.get('numInvalidAudioFiles')
        self.duration = media_dict.get('duration')
        self.size = media_dict.get('size')
        self.ebook_format = media_dict.get('ebookFormat')


class Audiobook:
    def __init__(self, data):
        self.id = data.get('id')
        self.ino = data.get('ino')
        self.old_library_item_id = data.get('oldLibraryItemId')
        self.library_id = data.get('libraryId')
        self.folder_id = data.get('folderId')
        self.path = data.get('path')
        self.rel_path = data.get('relPath')
        self.is_file = data.get('isFile')
        self.mtime_ms = data.get('mtimeMs')
        self.ctime_ms = data.get('ctimeMs')
        self.birthtime_ms = data.get('birthtimeMs')
        self.added_at = data.get('addedAt')
        self.updated_at = data.get('updatedAt')
        self.is_missing = data.get('isMissing')
        self.is_invalid = data.get('isInvalid')
        self.media_type = data.get('mediaType')
        self.media = Media(data.get('media', {}))
        self.num_files = data.get('numFiles')
        self.size = data.get('size')
