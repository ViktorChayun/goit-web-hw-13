from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count

from .forms import TagForm, QuoteForm, AuthorForm
from .models import Tag, Quote, Author
from .scrap_data.scrap import scrap_and_upload_data


def count_top_tags(number_of_tags=10, min_font_size=10, max_font_size=28):
    # Отримуємо топ-10 тегів за кількістю використань
    top_tags = Tag.objects.annotate(cnt=Count('quote'))\
        .order_by('-cnt')[:number_of_tags]
    # print(f"top tags: {top_tags}")
    # Визначаємо мінімальне та максимальне значення використання
    if top_tags:
        max_val = max(tag.cnt for tag in top_tags)
        min_val = min(tag.cnt for tag in top_tags)
    else:
        max_val = min_val = 0

    # розраховуємо розмір шрифту до кожного тегу
    for tag in top_tags:
        if max_val > min_val:
            # Масштабуємо розмір шрифту
            scale = (tag.cnt - min_val) / (max_val - min_val)
            tag.font_size = int(min_font_size + (max_font_size - min_font_size) * scale)
        else:
            # Якщо всі теги мають однакову частоту, встановлюємо мінімальний розмір
            tag.font_size = max_font_size

    return top_tags


def get_quotes_on_page(request):
    # Отримуємо кількість цитат на сторінку з параметра GET (за замовчуванням 5)
    quotes_per_page = request.GET.get('quotes_per_page', 5)
    try:
        quotes_per_page = int(quotes_per_page)
    except (ValueError, TypeError):
        # Якщо значення некоректне, використовуємо 10
        quotes_per_page = 10  # Якщо значення некоректне, використовуємо 10
    return quotes_per_page


# Create your views here.
def main(request):
    quotes_on_page = get_quotes_on_page(request)

    quotes = Quote.objects.all()
    # Отримуємо топ-10 тегів за кількістю використань
    top_tags = count_top_tags()

    # Отримуємо всі цитати, які належать користувачу
    if len(quotes) <= quotes_on_page:
        return render(
            request,
            'app_quote/index.html',
            {
                "page_obj": quotes,
                "top_tags": top_tags,
                'quotes_per_page': quotes_on_page,
            }
        )
    else:
        # Додаємо пагінацію (наприклад, 10 цитат на сторінку)
        paginator = Paginator(quotes, quotes_on_page)  # 5 цитат на сторінку
        page_number = request.GET.get('page')  # Отримуємо номер сторінки з параметра GET
        page_obj = paginator.get_page(page_number)  # Отримуємо об'єкт сторінки

        # Передаємо об'єкт сторінки в шаблон
        return render(
            request,
            'app_quote/index.html',
            {
                "page_obj": page_obj,
                "top_tags": top_tags,
                'quotes_per_page': quotes_on_page,
            }
        )


@login_required
# створення тегу
def tag(request):
    my_tags = Tag.objects.filter(user=request.user).all()

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            return redirect(to='app_quote:main')
        else:
            # not valid form --> render again
            return render(
                request,
                'app_quote/tag.html',
                {
                    'form': form,
                    'tags': my_tags,
                }
            )

    # get request
    return render(
        request,
        'app_quote/tag.html',
        {
            'form': TagForm(),
            'tags': my_tags,
        }
    )


@login_required
def quote(request, quote_id=None):
    # tags = Tag.objects.all()
    tags = Tag.objects.filter(user=request.user).all()
    authors = Author.objects.filter(user=request.user).all()

    if request.method == 'POST':
        print(f"POST request - {quote_id}")
        if quote_id:
            # редагування цитати
            quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
            form = QuoteForm(request.POST, instance=quote)
        else:
            # створення нової цитати
            form = QuoteForm(request.POST)

        if form.is_valid():
            new_quote = form.save(commit=False)
            new_quote.user = request.user
            # new_quote.save()

            # add author to quote
            author = Author.objects.get(
                id=request.POST.get('author'),
                user=request.user
            )
            new_quote.author = author
            new_quote.save()

            # add tags to quote (many to many --> stored in separate table)
            choice_tags = Tag.objects.filter(
                name__in=request.POST.getlist('tags'),
                user=request.user
            )
            for tag in choice_tags.iterator():
                new_quote.tags.add(tag)

            return redirect(to='app_quote:main')
        else:
            # якщо форма не валідна, повертаємо її знову а режимі редагування
            return render(
                request,
                'app_quote/quote.html',
                {
                    "tags": tags,
                    'authors': authors,
                    'form': form,
                    'quote': quote,
                }
            )
    else:
        # Якщо GET-запит, створюємо форму для редагування або створення
        if quote_id:
            # quote = get_object_or_404(Quote, pk=quote_id, user=request.user)
            quote = Quote.objects.filter(pk=quote_id, user=request.user).first()
            form = QuoteForm(instance=quote)
        else:
            quote = None
            form = QuoteForm()

        return render(
            request,
            'app_quote/quote.html',
            {
                "tags": tags,
                'authors': authors,
                'form': form,
                'quote': quote,
            }
        )


def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    if not quote or quote.user != request.user:
        msg = f"Quote (id={quote_id}) does not belong to the '{request.user}' user --> You can't see details here."
        return redirect(
            to='app_quote:error-page',
            message=msg
        )
    return render(request, 'app_quote/quote_detail.html', {"quote": quote})


@login_required
def quote_delete(request, quote_id):
    q = Quote.objects.filter(
        pk=quote_id,
        user=request.user
    ).first()
    # print(f"quote: {q}")

    if q:
        # якщо цитата належить користувачу, то видаляємо її
        q.delete()
        return redirect(to='app_quote:main')
    else:
        # print(f"Quote with id {quote_id} not found or does not belong to the user.")
        msg = f"Quote (id={quote_id}) does not belong to the '{request.user}' user --> Can't delete it."
        return redirect(
            to='app_quote:error-page',
            message=msg
        )


@login_required
# створення або редагування автора
def author(request, author_id=None):
    my_authors = Author.objects.filter(user=request.user).all()
    # print(f"my_authors: {my_authors}")
    # print(f"author_id: {author_id}")
    if request.method == 'POST':
        # print("POST request")
        # Якщо передано author_id, отримуємо існуючого автора або повертаємо 404
        if author_id:
            author = get_object_or_404(Author, pk=author_id, user=request.user)
            print(f"Loaded author: {author}")
            form = AuthorForm(request.POST, instance=author)
        else:
            # Якщо ID немає, створюємо нового автора
            form = AuthorForm(request.POST)

        if form.is_valid():
            author = form.save(commit=False)
            author.user = request.user
            print(f"author.= {author}, author.pk = {author.pk}")
            author.save()
            return redirect(to='app_quote:main')
        else:
            # Якщо форма не валідна, повертаємо її з помилками
            print(f"Error={form.errors}")
            return render(
                request,
                'app_quote/author.html',
                {
                    'form': form,
                    'authors': my_authors,
                }
            )
    else:
        # Якщо GET-запит, створюємо форму для редагування або створення
        print("GET request")
        if author_id:
            author = get_object_or_404(Author, pk=author_id, user=request.user)
        else:
            author = None
        form = AuthorForm(instance=author)
        return render(
            request,
            'app_quote/author.html',
            {
                'form': form,
                'authors': my_authors,
            }
        )


def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'app_quote/author_detail.html', {"author": author})


@login_required
def author_delete(request, author_id):
    Author.objects.get(
        pk=author_id,
        user=request.user
    ).delete()

    return redirect(to='app_quote:main')


@login_required
def scrap_data(request):
    scrap_and_upload_data(request.user.id)
    return redirect(to='app_quote:main')


def search_by_tag(request, tag_name):
    quotes_on_page = get_quotes_on_page(request)
    tag = get_object_or_404(Tag, name=tag_name)
    quotes = Quote.objects.filter(tags=tag).all()

    # Отримуємо топ-10 тегів за кількістю використань
    top_tags = count_top_tags()

    if len(quotes) <= quotes_on_page:
        return render(
            request,
            # 'app_quote/index.html',
            'app_quote/quotes_by_tag.html',
            {
                'tag': tag,
                "page_obj": quotes,
                "top_tags": top_tags,
                'quotes_per_page': quotes_on_page,
            }
        )
    else:
        # Додаємо пагінацію (наприклад, 10 цитат на сторінку)
        paginator = Paginator(quotes, quotes_on_page)
        # Отримуємо номер сторінки з параметра GET
        page_number = request.GET.get('page')
        # Отримуємо об'єкт сторінки
        page_obj = paginator.get_page(page_number)
        # Передаємо цитати та тег у шаблон
        return render(
            request,
            'app_quote/quotes_by_tag.html',
            {
                'tag': tag,
                'page_obj': page_obj,
                "top_tags": top_tags,
                'quotes_per_page': quotes_on_page,
            }
        )


def error(response, message):
    return render(
        response,
        'app_quote/error.html',
        {
            'message': message
        }
    )
