from time import sleep
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment


# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(
            username='trump',
            password='somepassword'
        )
        self.user_obama = User.objects.create_user(
            username='obama',
            password='somepassword'
        )
        self.user_obama.is_staff = True  # user_obama에게 staff 권한을 줌
        self.user_obama.save()  # user_obama에게 staff 권한을 준 채로 저장함

        self.category_programming = Category.objects.create(
            name='programming', slug='programming'
        )
        self.category_music = Category.objects.create(
            name='music', slug='music'
        )

        self.tag_python_kor = Tag.objects.create(
            name='파이썬 공부', slug='파이썬-공부'
        )
        self.tag_python = Tag.objects.create(
            name='python', slug='python'
        )
        self.tag_hello = Tag.objects.create(
            name='hello', slug='hello'
        )

        self.post_001 = Post.objects.create(
            title='첫번째 포스트입니다.',
            content='Hello, World. We are the World.',
            category=self.category_programming,
            author=self.user_trump
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두번째 포스트입니다.',
            content='저는 새우볶음밥을 좋아합니다.',
            category=self.category_music,
            author=self.user_obama
        )
        self.post_003 = Post.objects.create(
            title='세번째 포스트입니다.',
            content='카테고리가 없습니다.',
            author=self.user_obama
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_obama,
            content='첫 번째 댓글입니다.'
        )

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):  # id가 'category_card' 인 div 요소를 찾음,
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(
            f'{self.category_programming.name} ({self.category_programming.post_set.count()})',
                      categories_card.text
        )
        self.assertIn(
            f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text
        )
        self.assertIn(f'미분류 (1)', categories_card.text)

    def test_post_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')  # html.parser를 사용해서 soup에 넣을 것

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # 포스트가 없는

    def test_post_list_without_post(self):
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)
        # self.asser Equal(2, 2)
        #
        # # 1.1 포스트 목록 페이지(post list)를 연다.
        # response = self.client.get('/blog/')    #blog라는 url을 요청함
        #
        # # 1.2 정상적으로 페이지가 로드된다.
        # self.assertEqual(response.status_code, 200)
        # # 1.3 페이지의 타이틀에 Blog라는 문구가 있다.
        # soup = BeautifulSoup(response.content, 'html.parser') #html.parser를 사용해서 soup에 넣을 것
        # self.assertIn('Blog',soup.title.text)
        #
        # self.navbar_test(soup)
        #
        # # 2.1 게시물이 하나도 없을 때
        # self.assertEqual(Post.objects.count(), 0) # 몇 개의 게시물이 있는지 센다.
        # # 2.2 메인 영역에 "아직 게시물이 없습니다." 라는 문구가 나온다.
        # main_area = soup.find('div', id='main-area')
        # self.assertIn("아직 게시물이 없습니다.", main_area.text)
        #
        # # 3.1 만약 게시물이 2개 이상 있다면,
        # post_001 = Post.objects.create(
        #     title='첫번째 포스트입니다.',
        #     content='Hello, World. We are the World.',
        #     author=self.user_trump
        # )
        # post_002 = Post.objects.create(
        #     title='두번째 포스트입니다.',
        #     content='저는 새우볶음밥을 좋아합니다.',
        #     author=self.user_obama
        # )
        # self.assertEqual(Post.objects.count(), 2)
        #
        # # 3.2 포스트 목록 페이지를 새로 고침했을 때,
        # response = self.client.get('/blog/')
        # soup = BeautifulSoup(response.content, 'html.parser')
        # # 3.3 메인 영역에 포스트 2개의 타이틀이 존재한다.
        # main_area = soup.find('div', id='main-area')
        # self.assertIn(post_001.title, main_area.text)
        # self.assertIn(post_002.title, main_area.text)
        # # 3.4 "아직 게시물이 없습니다" 라는 문구가 없어야 한다.
        # self.assertNotIn("아직 게시물이 없습니다.", main_area.text)
        #
        # self.assertIn(self.user_trump.username.upper(), main_area.text)
        # self.assertIn(self.user_obama.username.upper(), main_area.text)

    def test_post_detail(self):
        self.assertEqual(Post.objects.count(), 3)
        # 1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다.(status code :200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        # 2.5 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.
        self.assertIn(self.user_trump.username.upper(), main_area.text)
        # 2.6 첫 번째 포스트의 내용이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)  # comment_001 안에 작성자 이름도 있게 할 것
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def tst_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

        # 로그인 하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())
        # 로그인하지 않은 상태에서 해당 페이지를 연다.
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html_parser')

        comment_area = soup.find('div', id='comment-area') # 상세페이지에서 답글이 적혀 있는 영역
        self.assertIn('Log in and leave a comment', comment_area.text)
        self.assertFalse(comment_area.find('form', id='comment-form'))
        # 로그인하지 않은 경우에는 id가 'comment-form'인 form이 존재하지 않아야 한다.

        # 로그인 한 상태
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html_parser')

        comment_area = soup.find('div', id='comment-area')  # 상세페이지에서 답글이 적혀 있는 영역
        self.assertNotIn('Log in and leave a comment', comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))
        response = self.client.post(
            self.post_001.get_absolute_url + 'new_comment/',
            {
                'content': '오바마의 댓글입니다.'
            },
            follow=True # 서버에서 post를 처리한 후 리다이렉트될 때, 따라가도록 설정해줌
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, ) # 새롭게 댓글이 달린 포스트페이지의 타이틀에 이름이 제대로 붙어있는지

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('obama', new_comment_div.text)
        self.assertIn('오바마의 댓글입니다.', new_comment_div.text)


    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content='트럼프의 댓글입니다.'
        )
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        # 로그인하지 않은 경우에는 수정 보튼이 보이지 않음
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))


        # obama로 로그인 한 상태
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertTrue(comment_area.find('a', id='comment-1-update-btn'))
        # 오바마로 로그인한 경우에는 오바마가 작성한 댓글의 수정버튼이 나타남
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))

        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')
        # 위의 href 주소(update_comment/pk값/) 이 댓글을 수정하는 페이지로 이동하는 주소가 되도록 설정

        response = self.client.get('/blog/update_comment/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Comment - Blog', soup.title.text)
        update_comment_form = soup.find('form', id='comment-form')
        # Edit Comment 페이지 안에는 하나의 댓글만 나타나기 때문에 pk를 작성할 필요가 없다.
        content_textarea = update_comment_form.find('textarea', id='id_content')
        # 장고에서 만드는 방식 / 해당 field의 id를 작성하고 그 이후에 '_content'를 붙여준다.
        self.assertIn(self.comment_001.content, content_textarea.text)
        sleep(2)

        response = self.client.post(
            '/blog/update_comment/1/',
            {
                'content': '오바마의 댓글을 수정합니다.'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('오바마의 댓글을 수정합니다.', comment_001_div.text)
        self.assertIn('Updated: ', comment_001_div.text)

    def test_comment_delete(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001,
            author = self.user_trump,
            content='트럼프의 댓글입니다.'
        )
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        # 로그인하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertFalse(comment_area.find('a', id="comment-2-delete-btn"))

        # trump로 로그인한 상태
        self.client.login(username="trump", password="somepassword")
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn')) # 오
        self.assertTrue(comment_area.find('a', id="comment-2-delete-btn"))

        comment_002_delete_modal_btn = comment_area.find('a', id='comment-2-delete-btn')
        self.assertIn('delete', comment_002_delete_modal_btn.text)
        self.assertEqual(
            comment_002_delete_modal_btn.attrs['data-target'],
            '#deleteCommentModal-2'  # 각 댓글의 삭제확인에 대한 modal을 pk로 구분할 수 있게끔 여러 개 만들어야 하낟.
        )

        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')
        self.assertIn('Are You Sure?', delete_comment_modal_002.text)
        # delete 버튼을 눌렀을 때 삭제확인 modal을 띄움
        really_delete_btn_002 = delete_comment_modal_002.find('a')
        self.assertIn('Delete', really_delete_btn_002.text)
        self.assertEqual(really_delete_btn_002.attrs['href'], '/blog/delete_comment/2/')

        response = self.client.get('/blog/delete_comment/2/', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertIn(self.post_001.title, soup.title.text) # 댓글 삭제 후 돌아온 페이지가 원래있던 페이지가 맞는지 확인
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('트럼프의 댓글입니다.', comment_area.text)

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())  # 해당 카테고리의 절대경로로 가도록 함
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.h1.text)
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)  # 별다른 조건이 없으면 존재하는지 확인

        self.assertIn(self.tag_hello.name, soup.h1.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post_without_login(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

    def test_create_post_with_login(self):
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)  # staff 권한이 없어서 들어갈 수 없다.

        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)  # staff 권한이 있어서 들어갈 수 있있.

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create a New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertEqual(Tag.objects.count(), 3) # 여기까지는 tag가 세 개 있었음

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': 'Post Form 페이지를 만듭시다.',
                'tags_str': 'new tag; 한글 태그, python'
            }
        )

        last_post = Post.objects.last()
        self.assertEqual(last_post.title, 'Post Form 만들기')
        self.assertEqual(last_post.author.username, 'obama')
        self.assertEqual(last_post.content, 'Post Form 페이지를 만듭시다.')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertTrue(Tag.objects.get(name='python'))
        self.assertEqual(Tag.objects.count(), 5) # 위의 3개의 태그 중 python을 제외한 태그 두 개가 추가되어 태그가 총 다섯 개가 됨

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 하지 않은 상태에서 접근 하는 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만, 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(username='trump', password='somepassword')
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200) # user_obama가 아니므로 정상실행이 되지 않음

        # 작성자(obama)가 접근하는 경우
        self.assertEqual(self.post_003.author, self.user_obama)
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200) # user_obama 이므로 정상적으로 실행됨
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다.',
                'content': '안녕 세계? 우리는 하나!',
                'category': self.category_music.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag'  # 위의 '파이썬 공부; python' 에서 'python'은 사라지고 '파이썬 공부' 만 남는지 확인
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('안녕 세계? 우리는 하나!', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)

        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_search(self):
        post_about_python = Post.objects.create(
            title = '파이썬에 대한 포스트입니다.',
            content = 'Hello World, We are the World.',
            author = self.user_trump
        )

        response = self.client.get('/blog/search/파이썬/') # 검색어를 서버에 전달하는 url
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')

        self.assertIn('Search: 파이썬 (2)', main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        self.assertIn(post_about_python.title, main_area.text)
