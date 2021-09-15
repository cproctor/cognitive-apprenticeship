TODO

- Alter models such that Manuscript has Reviewers through Reviews.

- Create fixture with fake students
- Built out editor views
- Build out editor submenu
  - Manuscripts (kanban-style flowchart)
    - Assign reviewers
  - Authors (shows stats on each author)
  - Reviewers (shows stats on each reviewer)

- Allow author to confirm authorship
- Manuscripts, not revisions, should have reviewers

- I need the concept of "issues"
  - Has an introduction
  - Has a publication date
  - Has a volume number
  - Has an issue number
  - Has manuscripts

- Each paper should also come with a prebuilt bibliographic entry; get students
  to start citing each others' papers.
  - Configure journal info in settings

- Add a profile-creation signal in roles

- Use FlatPage https://docs.djangoproject.com/en/3.2/ref/contrib/flatpages/ for
  About page. TinyMCE can be the editor. https://django-tinymce.readthedocs.io/en/latest/usage.html

- Email templates


## Documentation

- Reviewers are assigned to manuscripts, as they stay with manuscripts
  throughout the review process. This may include feedback on multiple
  revisions. 
