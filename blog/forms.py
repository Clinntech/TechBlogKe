from django import forms
from django.utils.text import slugify 
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Category, Comment, Post, Tag

class PostForm(forms.ModelForm):
    """Form used by authors and administrators to manage posts."""

    class Meta:
        model = Post

        fields = (
            "title",
            "slug",
            "excerpt",
            "content",
            "featured_image",
            "category",
            "tags",
            "meta_title",
            "meta_description",
            "status",
            "scheduled_at",
            "allow_comments",
            "is_featured",
        )

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Enter your article title (H1)"
                    ),
                }
            ),

            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "article-url-slug"
                    ),
                }
            ),

            "excerpt": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Write a short introduction "
                        "or article summary."
                    ),
                    "rows": 5,
                }
            ),


            "content": CKEditor5Widget(
                attrs={
                    "class": "django_ckeditor_5",
                },
                config_name="default",
            ),


            "featured_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": (
                        "image/jpeg,image/png,image/webp"
                    ),
                }
            ),


            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),


            "tags": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                    "size": 6,
                }
            ),


            "meta_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "SEO title (maximum 60 characters)"
                    ),
                    "maxlength": 60,
                }
            ),


            "meta_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "SEO description "
                        "(maximum 160 characters)"
                    ),
                    "rows": 3,
                    "maxlength": 160,
                }
            ),


            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "scheduled_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),


            "allow_comments": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),


            "is_featured": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }



    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs,
        )


        self.fields["category"].queryset = (
            Category.objects.order_by("name")
        )


        self.fields["tags"].queryset = (
            Tag.objects.order_by("name")
        )


        self.fields["category"].empty_label = (
            "Select a category"
        )



    def clean_title(self):

        title = self.cleaned_data["title"].strip()


        if len(title) < 5:

            raise forms.ValidationError(
                "The article title must contain at least 5 characters."
            )


        return title

def clean_slug(self):

    slug = self.cleaned_data.get(
        "slug"
    )


    if slug:

        slug = slugify(slug)


        existing_slug = Post.objects.filter(
            slug=slug
        )


        if self.instance.pk:

            existing_slug = existing_slug.exclude(
                pk=self.instance.pk
            )


        if existing_slug.exists():

            raise forms.ValidationError(
                "This URL slug is already in use."
            )


    return slug

    def clean_excerpt(self):

        excerpt = self.cleaned_data["excerpt"].strip()


        if len(excerpt) < 20:

            raise forms.ValidationError(
                "The article summary must contain at least 20 characters."
            )


        return excerpt



    def clean_content(self):

        content = self.cleaned_data["content"].strip()


        if len(content) < 100:

            raise forms.ValidationError(
                "The article content must contain at least 100 characters."
            )


        return content



    def clean_featured_image(self):

        image = self.cleaned_data.get(
            "featured_image"
        )


        if image and hasattr(image, "size"):

            maximum_size = 5 * 1024 * 1024


            if image.size > maximum_size:

                raise forms.ValidationError(
                    "The featured image must be smaller than 5 MB."
                )


        return image

class CommentForm(forms.ModelForm):
    """Form used by signed-in users to submit comments."""

    class Meta:

        model = Comment

        fields = (
            "content",
        )


        widgets = {

            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Join the discussion..."
                    ),
                    "rows": 4,
                    "maxlength": 1000,
                }
            ),
        }


        labels = {
            "content": "Your comment",
        }



    def clean_content(self):

        content = self.cleaned_data["content"].strip()


        if len(content) < 2:

            raise forms.ValidationError(
                "Your comment is too short."
            )


        return content

class CategoryForm(forms.ModelForm):
    """Form used by administrators to manage categories."""

    class Meta:

        model = Category

        fields = (
            "name",
            "description",
        )


        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Category name"
                    ),
                }
            ),


            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Describe this category."
                    ),
                    "rows": 4,
                }
            ),
        }

    def clean_name(self):

        name = self.cleaned_data["name"].strip()
        existing_category = Category.objects.filter(
            name__iexact=name
        )

        if self.instance.pk:

            existing_category = existing_category.exclude(
                pk=self.instance.pk
            )

        if existing_category.exists():

            raise forms.ValidationError(
                "A category with this name already exists."
            )

        return name

class TagForm(forms.ModelForm):
    """Form used by administrators to manage tags."""
    class Meta:

        model = Tag

        fields = (
            "name",
        )

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Tag name"
                    ),
                }
            ),
        }

    def clean_name(self):

        name = self.cleaned_data["name"].strip()
        existing_tag = Tag.objects.filter(
            name__iexact=name
        )

        if self.instance.pk:

            existing_tag = existing_tag.exclude(
                pk=self.instance.pk
            )

        if existing_tag.exists():

            raise forms.ValidationError(
                "A tag with this name already exists."
            )
        
        return name