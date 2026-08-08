from whitenoise.storage import CompressedManifestStaticFilesStorage

class NonStrictWhiteNoiseStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
