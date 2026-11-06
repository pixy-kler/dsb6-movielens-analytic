#!/usr/bin/env python3

import os
import re
import sys
import json
from collections import defaultdict
from datetime import datetime
# ================================================================
# КЛАСС MOVIES
# ================================================================

class Movies:
    def __init__(self, filepath, limit=1000):
        self.movies = []
        self._load_data(filepath, limit)
    
    def _load_data(self, filepath, n):
        """Загрузка первых n записей из файла movies.csv"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[1:], 1):
                    if i > n:
                        break
                    
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        movie_id = int(parts[0])
                        title = parts[1].strip()
                        genres = ','.join(parts[2:]).strip()
                        
                        self.movies.append({
                            'movieId': movie_id,
                            'title': title,
                            'genres': genres
                        })
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки файла {filepath}: {e}")
    
    def extract_year(self, title):
        """Извлечение года из названия с помощью регулярного выражения"""
        try:
            match = re.search(r'\b[12]\d{3}\b', title)
            return int(match.group()) if match else None
        except Exception:
            return None
    
    def get_movies_with_years(self):
        """Возвращает список фильмов с извлечёнными годами"""
        result = []
        for m in self.movies:
            year = self.extract_year(m['title'])
            result.append((m['title'], year, m['genres']))
        return result
    
    def sort_by_year(self, reverse=False):
        """Сортировка фильмов по году выпуска"""
        def get_year(m):
            year = self.extract_year(m['title'])
            return year if year is not None else (-1 if not reverse else 9999)
        
        try:
            return sorted(self.movies, key=get_year, reverse=reverse)
        except Exception:
            return self.movies
    
    def sort_by_title(self, reverse=False):
        """Сортировка фильмов по названию (без года в конце)"""
        def clean_title(m):
            title = m['title']
            cleaned = re.sub(r'\s*[\(\[]?[12]\d{3}[\)\]]?\s*$', '', title)
            return cleaned.lower()
        
        try:
            return sorted(self.movies, key=clean_title, reverse=reverse)
        except Exception:
            return self.movies
    
    def filter_by_genre(self, genre):
        """Фильтрация фильмов по жанру"""
        try:
            genre_lower = genre.lower()
            result = []
            for m in self.movies:
                genres_lower = m['genres'].lower()
                if genre_lower in genres_lower.split('|'):
                    result.append(m)
            return result
        except Exception:
            return []
    
    def get_decade_stats(self):
        """Статистика по десятилетиям"""
        try:
            stats = {}
            for m in self.movies:
                year = self.extract_year(m['title'])
                if year:
                    decade = (year // 10) * 10
                    stats[decade] = stats.get(decade, 0) + 1
            return dict(sorted(stats.items()))
        except Exception:
            return {}
    
    def search_by_title_pattern(self, pattern, use_regex=False):
        """Поиск фильмов по шаблону названия"""
        try:
            if use_regex:
                regex = re.compile(pattern, re.IGNORECASE)
                return [m for m in self.movies if regex.search(m['title'])]
            else:
                pattern_lower = pattern.lower()
                return [m for m in self.movies if pattern_lower in m['title'].lower()]
        except Exception:
            return []
    
    def get_summary_stats(self):
        """Сводная статистика по фильмам"""
        try:
            years = [self.extract_year(m['title']) for m in self.movies]
            valid_years = [y for y in years if y is not None]
            
            genre_count = {}
            for m in self.movies:
                for genre in m['genres'].split('|'):
                    if genre != '(no genres listed)':
                        genre_count[genre] = genre_count.get(genre, 0) + 1
            
            top_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'total_movies': len(self.movies),
                'movies_with_year': len(valid_years),
                'movies_without_year': len(self.movies) - len(valid_years),
                'oldest_movie': min(valid_years) if valid_years else None,
                'newest_movie': max(valid_years) if valid_years else None,
                'unique_genres': len(genre_count),
                'top_genres': top_genres
            }
        except Exception:
            return {'total_movies': len(self.movies), 'error': 'Ошибка подсчёта статистики'}


# ================================================================
# КЛАСС LINKS
# ================================================================

class Links:
    def __init__(self, filepath, limit=1000):
        self.filepath = filepath
        self.limit = limit
        self.data = []
        self._load()
    
    def _load(self):
        """Загрузка первых limit записей из файла links.csv"""
        try:
            with open(self.filepath, 'r') as f:
                # Читаем заголовок
                header = f.readline().strip().split(',')
                # Находим индексы нужных колонок
                movie_id_idx = header.index('movieId') if 'movieId' in header else 0
                imdb_id_idx = header.index('imdbId') if 'imdbId' in header else 1
                tmdb_id_idx = header.index('tmdbId') if 'tmdbId' in header else 2
                for i, line in enumerate(f):
                    if i >= self.limit:
                        break
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        tmdb = int(parts[tmdb_id_idx]) if parts[tmdb_id_idx] and parts[tmdb_id_idx] != '' else None
                        self.data.append({
                            'movieId': int(parts[movie_id_idx]),
                            'imdbId': parts[imdb_id_idx],
                            'tmdbId': tmdb
                        })
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки файла {self.filepath}: {e}")
    
    def get_all(self):
        """Возвращает копию всех данных"""
        return self.data.copy()
    
    def get_by_movie_id(self, movie_id):
        """Ищет запись по movieId"""
        for item in self.data:
            if item['movieId'] == movie_id:
                return item.copy()
        return None
    
    def get_movies_without_tmdb(self):
        """Возвращает список фильмов без tmdbId (отсортированный)"""
        result = [item['movieId'] for item in self.data if item['tmdbId'] is None]
        return sorted(result)
    
    def get_stats(self):
        """Возвращает статистику по ссылкам"""
        total = len(self.data)
        with_tmdb = sum(1 for x in self.data if x['tmdbId'] is not None)
        return {
            'total': total,
            'with_tmdb': with_tmdb,
            'without_tmdb': total - with_tmdb
        }
    
    def find_missing_ids(self):
        """Находит пропущенные movieId в диапазоне от 1 до максимального"""
        if not self.data:
            return []
        
        existing_ids = set(item['movieId'] for item in self.data)
        min_id = min(existing_ids)
        max_id = max(existing_ids)
        
        missing = []
        for movie_id in range(min_id, max_id + 1):
            if movie_id not in existing_ids:
                missing.append(movie_id)
        
        return missing
    
    def get_imdb_url(self, movie_id):
        """Генерирует ссылку на IMDb"""
        link = self.get_by_movie_id(movie_id)
        if link:
            imdb_clean = link['imdbId'].lstrip('0')
            return f"https://www.imdb.com/title/tt{imdb_clean}/"
        return None
    
    def sort_by_imdb_id(self, reverse=False):
        """Сортирует данные по imdbId"""
        sorted_data = sorted(self.data, key=lambda x: x['imdbId'], reverse=reverse)
        return [item.copy() for item in sorted_data]
    
    def sort_by_tmdb_id(self, reverse=False):
        """Сортирует данные по tmdbId (None значения в конце)"""
        if reverse:
            sorted_data = sorted(self.data, key=lambda x: (x['tmdbId'] is not None, x['tmdbId']), reverse=True)
        else:
            sorted_data = sorted(self.data, key=lambda x: (x['tmdbId'] is None, x['tmdbId']))
        return [item.copy() for item in sorted_data]
    
    def get_id_range_report(self):
        """Формирует отчёт о диапазоне ID с отметками о пропусках"""
        if not self.data:
            return []
        
        existing_ids = set(item['movieId'] for item in self.data)
        min_id = min(existing_ids)
        max_id = max(existing_ids)
        
        report = []
        for movie_id in range(min_id, max_id + 1):
            if movie_id in existing_ids:
                report.append(movie_id)
            else:
                report.append('zero')
        
        return report
    
    def compare_with_full_range(self, start_id=1, end_id=None):
        """Сравнивает существующие ID с полным диапазоном"""
        existing_ids = set(item['movieId'] for item in self.data)
        
        if end_id is None:
            end_id = max(existing_ids) if existing_ids else start_id
        
        full_range = set(range(start_id, end_id + 1))
        missing_ids = full_range - existing_ids
        extra_ids = existing_ids - full_range
        
        return {
            'range_start': start_id,
            'range_end': end_id,
            'total_in_range': len(full_range),
            'existing_in_range': len(existing_ids & full_range),
            'missing_in_range': len(missing_ids),
            'missing_ids': sorted(list(missing_ids)),
            'outside_range': sorted(list(extra_ids)) if extra_ids else []
        }


# ================================================================
# КЛАСС RATINGS
# ================================================================

class Ratings:
    def __init__(self, filepath, limit=1000):
        self.filepath = filepath
        self.limit = limit
        self.data = []
        self._load()
    
    def _load(self):
        """Загрузка первых limit записей из файла ratings.csv"""
        try:
            with open(self.filepath, 'r') as f:
                header = f.readline().strip().split(',')
                # Находим индексы нужных колонок
                user_id_idx = header.index('userId') if 'userId' in header else 0
                movie_id_idx = header.index('movieId') if 'movieId' in header else 1
                rating_idx = header.index('rating') if 'rating' in header else 2
                timestamp_idx = header.index('timestamp') if 'timestamp' in header else 3
                
                for i, line in enumerate(f):
                    if i >= self.limit:
                        break
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        self.data.append({
                            'userId': int(parts[user_id_idx]),
                            'movieId': int(parts[movie_id_idx]),
                            'rating': float(parts[rating_idx]),
                            'timestamp': int(parts[timestamp_idx])
                        })
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки файла {self.filepath}: {e}")
    
    def get_all(self):
        """Возвращает копию всех оценок"""
        return self.data.copy()
    
    def get_by_user(self, user_id):
        """Возвращает все оценки пользователя"""
        return [x.copy() for x in self.data if x['userId'] == user_id]
    
    def get_by_movie(self, movie_id):
        """Возвращает все оценки фильма"""
        return [x.copy() for x in self.data if x['movieId'] == movie_id]
    
    def get_avg_rating(self, movie_id):
        """Средняя оценка фильма"""
        ratings = self.get_by_movie(movie_id)
        if not ratings:
            return None
        return round(sum(r['rating'] for r in ratings) / len(ratings), 2)
    
    def get_user_avg(self, user_id):
        """Средняя оценка пользователя"""
        ratings = self.get_by_user(user_id)
        if not ratings:
            return None
        return round(sum(r['rating'] for r in ratings) / len(ratings), 2)
    
    def get_top_movies(self, n=10):
        """Возвращает топ N фильмов по взвешенному рейтингу (Bayesian average)"""
        movie_ratings = defaultdict(list)
        for r in self.data:
            movie_ratings[r['movieId']].append(r['rating'])
        
        all_ratings = [r['rating'] for r in self.data]
        global_avg = sum(all_ratings) / len(all_ratings)
        
        total_movies = len(movie_ratings)
        total_ratings = len(self.data)
        confidence = total_ratings / total_movies if total_movies > 0 else 1
        
        result = []
        for movie_id, ratings in movie_ratings.items():
            count = len(ratings)
            avg = sum(ratings) / count
            
            weighted_avg = (count * avg + confidence * global_avg) / (count + confidence)
            
            result.append({
                'movie_id': movie_id,
                'weighted_rating': round(weighted_avg, 2),
                'avg_rating': round(avg, 2),
                'rating_count': count
            })
        
        result.sort(key=lambda x: x['weighted_rating'], reverse=True)
        
        top_n = result[:n] if n <= len(result) else result
        
        return [(item['movie_id'], item['weighted_rating'], item['avg_rating'], item['rating_count']) 
                for item in top_n]
    
    def get_stats(self):
        """Общая статистика по оценкам"""
        ratings_list = [r['rating'] for r in self.data]
        return {
            'total': len(self.data),
            'unique_users': len(set(r['userId'] for r in self.data)),
            'unique_movies': len(set(r['movieId'] for r in self.data)),
            'avg_rating': round(sum(ratings_list) / len(ratings_list), 2),
            'min_rating': min(ratings_list),
            'max_rating': max(ratings_list)
        }
    
    def convert_timestamps(self, ratings_list=None):
        """Конвертирует timestamp в datetime"""
        if ratings_list is None:
            ratings_list = self.data
        
        result = []
        for rating in ratings_list:
            rating_copy = rating.copy()
            rating_copy['datetime'] = datetime.fromtimestamp(rating_copy['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            result.append(rating_copy)
        
        return result
    

# ================================================================
# КЛАСС TAGS
# ================================================================

class Tags:
    def __init__(self, filepath, limit=1000):
        self.filepath = filepath
        self.limit = limit
        self.data = []
        self._load()
    
    def _load(self):
        """Загрузка первых limit записей из файла tags.csv"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Читаем заголовок
                header = f.readline().strip().split(',')
                # Находим индексы нужных колонок
                user_id_idx = header.index('userId') if 'userId' in header else 0
                movie_id_idx = header.index('movieId') if 'movieId' in header else 1
                tag_idx = header.index('tag') if 'tag' in header else 2
                timestamp_idx = header.index('timestamp') if 'timestamp' in header else 3
                
                for i, line in enumerate(f):
                    if i >= self.limit:
                        break
                    parts = line.strip().split(',')
                    # Обработка случая, когда в теге есть запятые (маловероятно, но учтём)
                    if len(parts) >= 4:
                        # Если тег содержит запятые, он мог быть разбит
                        # Склеиваем обратно всё, что после movieId до timestamp
                        tag_parts = parts[tag_idx:timestamp_idx] if timestamp_idx > tag_idx else [parts[tag_idx]]
                        tag = ','.join(tag_parts).strip()
                        
                        self.data.append({
                            'userId': int(parts[user_id_idx]),
                            'movieId': int(parts[movie_id_idx]),
                            'tag': tag,
                            'timestamp': int(parts[timestamp_idx] if timestamp_idx < len(parts) else parts[-1])
                        })
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки файла {self.filepath}: {e}")
    
    def get_all(self):
        """Возвращает копию всех тегов"""
        return self.data.copy()
    
    def get_by_user(self, user_id):
        """
        Возвращает все теги, добавленные конкретным пользователем
        """
        return [x.copy() for x in self.data if x['userId'] == user_id]
    
    def get_by_movie(self, movie_id):
        """
        Возвращает все теги, добавленные к конкретному фильму
        """
        return [x.copy() for x in self.data if x['movieId'] == movie_id]
    
    def get_unique_tags(self):
        """
        Возвращает все уникальные теги (без учёта регистра)
        """
        unique = set(tag['tag'].lower() for tag in self.data)
        return sorted(list(unique))
    
    def get_tag_count(self, tag):
        """
        Возвращает количество использований конкретного тега
        """
        tag_lower = tag.lower()
        return sum(1 for t in self.data if t['tag'].lower() == tag_lower)
    
    def get_most_popular_tags(self, n=10):
        """
        Возвращает топ N самых популярных тегов
        """
        tag_counts = defaultdict(int)
        for item in self.data:
            tag_lower = item['tag'].lower()
            tag_counts[tag_lower] += 1
        
        result = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return result[:n]
    
    def get_user_tagging_activity(self, user_id):
        """
        Возвращает статистику активности пользователя по тегированию
        """
        user_tags = self.get_by_user(user_id)
        if not user_tags:
            return {
                'user_id': user_id,
                'total_tags': 0,
                'unique_tags': 0,
                'unique_movies': 0
            }
        
        unique_tags = set(t['tag'].lower() for t in user_tags)
        unique_movies = set(t['movieId'] for t in user_tags)
        
        return {
            'user_id': user_id,
            'total_tags': len(user_tags),
            'unique_tags': len(unique_tags),
            'unique_movies': len(unique_movies)
        }
    
    def get_movie_tag_summary(self, movie_id):
        """
        Возвращает сводку по тегам фильма
        """
        movie_tags = self.get_by_movie(movie_id)
        if not movie_tags:
            return {
                'movie_id': movie_id,
                'total_tags': 0,
                'unique_tags': [],
                'tag_count': {}
            }
        
        tag_counts = defaultdict(int)
        for item in movie_tags:
            tag_counts[item['tag']] += 1
        
        return {
            'movie_id': movie_id,
            'total_tags': len(movie_tags),
            'unique_tags': sorted(list(set(t['tag'] for t in movie_tags))),
            'tag_count': dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
        }
    
    def search_tags(self, pattern, use_regex=False):
        """
        Поиск тегов по шаблону
        """
        try:
            if use_regex:
                regex = re.compile(pattern, re.IGNORECASE)
                return [t.copy() for t in self.data if regex.search(t['tag'])]
            else:
                pattern_lower = pattern.lower()
                return [t.copy() for t in self.data if pattern_lower in t['tag'].lower()]
        except Exception:
            return []
    
    def get_stats(self):
        """
        Возвращает общую статистику по тегам
        """
        unique_users = len(set(t['userId'] for t in self.data))
        unique_movies = len(set(t['movieId'] for t in self.data))
        unique_tags = len(set(t['tag'].lower() for t in self.data))
        
        return {
            'total_tags': len(self.data),
            'unique_users': unique_users,
            'unique_movies': unique_movies,
            'unique_tags': unique_tags,
            'avg_tags_per_movie': round(len(self.data) / unique_movies, 2) if unique_movies > 0 else 0,
            'avg_tags_per_user': round(len(self.data) / unique_users, 2) if unique_users > 0 else 0
        }
    
    def convert_timestamps(self, tags_list=None):
        """
        Конвертирует timestamp в читаемый формат datetime
        """
        if tags_list is None:
            tags_list = self.data
        
        result = []
        for tag in tags_list:
            tag_copy = tag.copy()
            tag_copy['datetime'] = datetime.fromtimestamp(tag_copy['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            result.append(tag_copy)
        
        return result
    

    
# ================================================================
# PYTEST ТЕСТЫ
# ================================================================

import pytest

# Фикстуры для тестов
@pytest.fixture
def temp_movies_file(tmp_path):
    """Создаёт временный файл movies.csv для тестов"""
    movies_file = tmp_path / "movies.csv"
    content = """movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
2,Jumanji (1995),Adventure|Children|Fantasy
3,Grumpier Old Men (1995),Comedy|Romance
4,Waiting to Exhale (1995),Comedy|Drama|Romance
5,Father of the Bride Part II (1995),Comedy"""
    movies_file.write_text(content)
    return str(movies_file)


@pytest.fixture
def temp_links_file(tmp_path):
    """Создаёт временный файл links.csv для тестов"""
    links_file = tmp_path / "links.csv"
    content = """movieId,imdbId,tmdbId
1,0114709,862
2,0113497,
3,0113228,15602
4,0114885,31357
5,0113041,11862"""
    links_file.write_text(content)
    return str(links_file)


@pytest.fixture
def temp_ratings_file(tmp_path):
    """Создаёт временный файл ratings.csv для тестов"""
    ratings_file = tmp_path / "ratings.csv"
    content = """userId,movieId,rating,timestamp
1,1,4.0,964982703
1,2,5.0,964982704
2,1,3.0,964982705
2,3,4.5,964982706
3,1,5.0,964982707
3,2,4.0,964982708
4,4,3.5,964982709
4,5,4.0,964982710
5,1,4.5,964982711"""
    ratings_file.write_text(content)
    return str(ratings_file)

@pytest.fixture
def temp_tags_file(tmp_path):
    """Создаёт временный файл tags.csv для тестов"""
    tags_file = tmp_path / "tags.csv"
    content = """userId,movieId,tag,timestamp
2,60756,funny,1445714994
2,60756,Highly quotable,1445714996
2,60756,will ferrell,1445714992
2,89774,Boxing story,1445715207
2,89774,MMA,1445715200
2,89774,Tom Hardy,1445715205
2,106782,drugs,1445715054
2,106782,Leonardo DiCaprio,1445715051
2,106782,Martin Scorsese,1445715056
7,48516,way too long,1169687325
18,431,Al Pacino,1462138765
18,431,gangster,1462138749
18,431,mafia,1462138755
18,1221,Al Pacino,1461699306
18,1221,Mafia,1461699303
18,5995,holocaust,1455735472
18,5995,true story,1455735479
18,44665,twist ending,1456948283
18,52604,Anthony Hopkins,1457650696
18,52604,courtroom drama,1457650711
18,52604,twist ending,1457650682
18,88094,britpop,1457444500"""
    tags_file.write_text(content, encoding='utf-8')
    return str(tags_file)


# ===== ТЕСТЫ ДЛЯ КЛАССА MOVIES =====

class TestMovies:
    
    def test_extract_year_returns_int_or_none(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        for movie in movies.movies[:5]:
            year = movies.extract_year(movie['title'])
            assert year is None or isinstance(year, int)
    
    def test_get_movies_with_years_returns_correct_types(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        result = movies.get_movies_with_years()
        assert isinstance(result, list)
        
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3
            assert isinstance(item[0], str)
            assert item[1] is None or isinstance(item[1], int)
            assert isinstance(item[2], str)
    
    def test_sort_by_year_ascending(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        sorted_movies = movies.sort_by_year(reverse=False)
        
        years = []
        for m in sorted_movies:
            year = movies.extract_year(m['title'])
            if year is not None:
                years.append(year)
        
        for i in range(len(years) - 1):
            assert years[i] <= years[i + 1]
    
    def test_sort_by_year_descending(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        sorted_movies = movies.sort_by_year(reverse=True)
        
        years = []
        for m in sorted_movies:
            year = movies.extract_year(m['title'])
            if year is not None:
                years.append(year)
        
        for i in range(len(years) - 1):
            assert years[i] >= years[i + 1]
    
    def test_filter_by_genre_returns_list_of_dicts(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        result = movies.filter_by_genre("Comedy")
        assert isinstance(result, list)
        
        for movie in result:
            assert isinstance(movie, dict)
            assert 'movieId' in movie
            assert isinstance(movie['movieId'], int)
    
    def test_year_extraction_edge_cases(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        assert movies.extract_year("Toy Story (1995)") == 1995
        assert movies.extract_year("Movie [2000]") == 2000
        assert movies.extract_year("No Year Here") is None
    
    def test_get_decade_stats_returns_dict(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        result = movies.get_decade_stats()
        assert isinstance(result, dict)
    
    def test_search_by_title_pattern(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        result = movies.search_by_title_pattern("Story")
        assert isinstance(result, list)
    
    def test_get_summary_stats_returns_dict(self, temp_movies_file):
        movies = Movies(temp_movies_file, limit=10)
        result = movies.get_summary_stats()
        assert isinstance(result, dict)
        assert 'total_movies' in result


# ===== ТЕСТЫ ДЛЯ КЛАССА LINKS =====

class TestLinks:
    
    def test_get_all_returns_list(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_all()
        assert isinstance(result, list)
    
    def test_get_all_elements_are_dicts(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_all()
        for item in result:
            assert isinstance(item, dict)
    
    def test_get_all_elements_have_correct_types(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_all()
        for item in result:
            assert isinstance(item['movieId'], int)
            assert isinstance(item['imdbId'], str)
            assert item['tmdbId'] is None or isinstance(item['tmdbId'], int)
    
    def test_get_by_movie_id_returns_dict(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_by_movie_id(1)
        assert isinstance(result, dict)
    
    def test_get_by_movie_id_returns_none_if_not_found(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_by_movie_id(999)
        assert result is None
    
    def test_get_movies_without_tmdb_returns_list(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_movies_without_tmdb()
        assert isinstance(result, list)
    
    def test_get_movies_without_tmdb_elements_are_ints(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_movies_without_tmdb()
        for item in result:
            assert isinstance(item, int)
    
    def test_get_movies_without_tmdb_is_sorted(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_movies_without_tmdb()
        assert result == sorted(result)
    
    def test_get_stats_returns_dict(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_stats()
        assert isinstance(result, dict)
    
    def test_find_missing_ids_returns_list(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.find_missing_ids()
        assert isinstance(result, list)
    
    def test_find_missing_ids_is_sorted(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.find_missing_ids()
        assert result == sorted(result)
    
    def test_sort_by_imdb_id(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.sort_by_imdb_id()
        assert isinstance(result, list)
        # Проверяем сортировку
        imdb_ids = [item['imdbId'] for item in result]
        assert imdb_ids == sorted(imdb_ids)
    
    def test_get_id_range_report(self, temp_links_file):
        links = Links(temp_links_file)
        result = links.get_id_range_report()
        assert isinstance(result, list)


# ===== ТЕСТЫ ДЛЯ КЛАССА RATINGS =====

class TestRatings:
    
    def test_get_all_returns_list(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_all()
        assert isinstance(result, list)
    
    def test_get_all_elements_are_dicts(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_all()
        for item in result:
            assert isinstance(item, dict)
    
    def test_get_all_elements_have_correct_types(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_all()
        for item in result:
            assert isinstance(item['userId'], int)
            assert isinstance(item['movieId'], int)
            assert isinstance(item['rating'], float)
            assert isinstance(item['timestamp'], int)
    
    def test_get_by_user_returns_list(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_by_user(1)
        assert isinstance(result, list)
    
    def test_get_by_user_elements_have_correct_user_id(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_by_user(1)
        for item in result:
            assert item['userId'] == 1
    
    def test_get_by_movie_returns_list(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_by_movie(1)
        assert isinstance(result, list)
    
    def test_get_avg_rating_returns_float(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_avg_rating(1)
        assert isinstance(result, float)
    
    def test_get_avg_rating_returns_none_if_no_ratings(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_avg_rating(999)
        assert result is None
    
    def test_get_user_avg_returns_float(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_user_avg(1)
        assert isinstance(result, float)
    
    def test_get_top_movies_returns_list(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_top_movies(3)
        assert isinstance(result, list)
    
    def test_get_top_movies_elements_are_tuples(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_top_movies(3)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 4
    
    def test_get_top_movies_is_sorted_correctly(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_top_movies(5)
        for i in range(len(result) - 1):
            assert result[i][1] >= result[i+1][1]
    
    def test_get_stats_returns_dict(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.get_stats()
        assert isinstance(result, dict)
    
    def test_convert_timestamps(self, temp_ratings_file):
        ratings = Ratings(temp_ratings_file)
        result = ratings.convert_timestamps(ratings.get_all()[:2])
        assert isinstance(result, list)
        assert 'datetime' in result[0]


# ===== ТЕСТЫ ДЛЯ КЛАССА TAGS =====

class TestTags:
    
    def test_get_all_returns_list(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_all()
        assert isinstance(result, list)
        assert len(result) == 22
    
    def test_get_all_elements_are_dicts(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_all()
        for item in result:
            assert isinstance(item, dict)
    
    def test_get_all_elements_have_correct_types(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_all()
        for item in result:
            assert isinstance(item['userId'], int)
            assert isinstance(item['movieId'], int)
            assert isinstance(item['tag'], str)
            assert isinstance(item['timestamp'], int)
    
    def test_get_by_user_returns_list(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_by_user(2)
        assert isinstance(result, list)
        assert len(result) == 9
    
    def test_get_by_user_elements_have_correct_user_id(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_by_user(2)
        for item in result:
            assert item['userId'] == 2
    
    def test_get_by_movie_returns_list(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_by_movie(60756)
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_get_by_movie_elements_have_correct_movie_id(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_by_movie(60756)
        for item in result:
            assert item['movieId'] == 60756
    
    def test_get_unique_tags_returns_list(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_unique_tags()
        assert isinstance(result, list)
        # Проверяем, что все элементы - строки
        for item in result:
            assert isinstance(item, str)
    
    def test_get_unique_tags_are_unique(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_unique_tags()
        assert len(result) == len(set(result))
    
    def test_get_unique_tags_is_sorted(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_unique_tags()
        assert result == sorted(result)
    
    def test_get_tag_count_returns_int(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_tag_count("funny")
        assert isinstance(result, int)
        assert result == 1
        
        result = tags.get_tag_count("Al Pacino")
        assert result == 2
    
    def test_get_tag_count_is_case_insensitive(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result1 = tags.get_tag_count("mafia")
        result2 = tags.get_tag_count("Mafia")
        assert result1 == result2 == 2
    
    def test_get_most_popular_tags_returns_list(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_most_popular_tags(5)
        assert isinstance(result, list)
    
    def test_get_most_popular_tags_elements_are_tuples(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_most_popular_tags(5)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], int)
    
    def test_get_most_popular_tags_is_sorted_correctly(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_most_popular_tags(5)
        for i in range(len(result) - 1):
            assert result[i][1] >= result[i+1][1]
    
    def test_get_user_tagging_activity_returns_dict(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_user_tagging_activity(2)
        assert isinstance(result, dict)
        assert result['user_id'] == 2
        assert result['total_tags'] == 9
        assert result['unique_tags'] == 9
        assert result['unique_movies'] == 3
    
    def test_get_user_tagging_activity_for_unknown_user(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_user_tagging_activity(999)
        assert result['user_id'] == 999
        assert result['total_tags'] == 0
    
    def test_get_movie_tag_summary_returns_dict(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_movie_tag_summary(60756)
        assert isinstance(result, dict)
        assert result['movie_id'] == 60756
        assert result['total_tags'] == 3
        assert len(result['unique_tags']) == 3
    
    def test_get_movie_tag_summary_for_unknown_movie(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_movie_tag_summary(999)
        assert result['movie_id'] == 999
        assert result['total_tags'] == 0
        assert result['unique_tags'] == []
    
    def test_search_tags_returns_list(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.search_tags("Al")
        assert isinstance(result, list)
        # Должен найти "Al Pacino" (2 раза)
        assert len(result) == 2
    
    def test_search_tags_case_insensitive(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result1 = tags.search_tags("funny")
        result2 = tags.search_tags("FUNNY")
        assert len(result1) == len(result2) == 1
    
    def test_search_tags_with_regex(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        # Ищем теги, начинающиеся на "maf" (mafia, Mafia)
        result = tags.search_tags(r'^maf', use_regex=True)
        assert len(result) == 2
    
    def test_get_stats_returns_dict(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_stats()
        assert isinstance(result, dict)
        assert 'total_tags' in result
        assert 'unique_users' in result
        assert 'unique_movies' in result
        assert 'unique_tags' in result
    
    def test_get_stats_values_have_correct_types(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.get_stats()
        assert isinstance(result['total_tags'], int)
        assert isinstance(result['unique_users'], int)
        assert isinstance(result['unique_movies'], int)
        assert isinstance(result['unique_tags'], int)
        assert isinstance(result['avg_tags_per_movie'], float)
        assert isinstance(result['avg_tags_per_user'], float)
    
    def test_convert_timestamps(self, temp_tags_file):
        tags = Tags(temp_tags_file)
        result = tags.convert_timestamps(tags.get_all()[:3])
        assert isinstance(result, list)
        for item in result:
            assert 'datetime' in item
            assert isinstance(item['datetime'], str)
            # Проверяем формат YYYY-MM-DD HH:MM:SS
            assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', item['datetime'])
    
    def test_limit_works(self, temp_tags_file):
        """Проверяет, что параметр limit работает корректно"""
        tags = Tags(temp_tags_file, limit=10)
        assert len(tags.data) == 10
        assert len(tags.get_all()) == 10


# ================================================================
# ТОЧКИ ВХОДА
# ================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Запуск тестов
        sys.exit(pytest.main([__file__, '-v', '--tb=short']))
    else:
        # Примеры использования
        print("=" * 60)
        print("MOVIELENS ANALYSIS MODULE")
        print("=" * 60)
        
        # Movies
        print("\n📽️  MOVIES:")
        movies_data = Movies("ml-latest-small/movies.csv", limit=1000)
        print(f"  Загружено фильмов: {len(movies_data.movies)}")
        print(f"  Статистика: {movies_data.get_summary_stats()}")
        
        # Links
        print("\n🔗 LINKS:")
        links_data = Links("ml-latest-small/links.csv")
        print(f"  Загружено ссылок: {len(links_data.get_all())}")
        print(f"  Статистика: {links_data.get_stats()}")
        print(f"  Пропущенные ID: {links_data.find_missing_ids()[:10]}...")
        
        # Ratings
        print("\n⭐ RATINGS:")
        ratings_data = Ratings("ml-latest-small/ratings.csv")
        print(f"  Загружено оценок: {len(ratings_data.get_all())}")
        print(f"  Статистика: {ratings_data.get_stats()}")
        
        top5 = ratings_data.get_top_movies(5)
        print(f"  Топ-5 фильмов (взвешенный рейтинг):")
        for i, (movie_id, weighted, avg, count) in enumerate(top5, 1):
            print(f"    {i}. Movie {movie_id}: weighted={weighted}, avg={avg}, count={count}")

        # Tags
        print("\n🏷️  TAGS:")
        tags_data = Tags("ml-latest-small/tags.csv")
        print(f"  Загружено тегов: {len(tags_data.get_all())}")
        print(f"  Статистика: {tags_data.get_stats()}")
        print(f"  Уникальные теги (первые 10): {tags_data.get_unique_tags()[:10]}")
        print(f"  Самые популярные теги: {tags_data.get_most_popular_tags(5)}")

        # Пример: теги для конкретного фильма
        movie_tags = tags_data.get_movie_tag_summary(60756)
        print(f"  Теги фильма 60756: {movie_tags}")
        
        print("\n✅ Готово!")

# 1250