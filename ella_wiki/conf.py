from ella.utils.settings import Settings

REDIS = {}

IS_MODERATOR_FUNC = lambda u: u.is_staff

wiki_settings = Settings('ella_wiki.conf', 'WIKI')
