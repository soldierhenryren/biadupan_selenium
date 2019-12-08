from peewee import IntegerField,CharField, AutoField, UUIDField, FloatField

from dbconfig import BaseModel,db

class cet4(BaseModel):
    id = IntegerField(default=0, primary_key=True)
    wordliteral = CharField()
    trasslate = CharField()
    voiceid = IntegerField()
    tpos = CharField()  # 词性
    tps = CharField()  # 音标
    class Meta:
        db_table = 'cet4'


class comcet4(BaseModel):
    id = IntegerField(default=0, primary_key=True)
    fristid = IntegerField()
    secondid = IntegerField()
    precom = IntegerField()
    tagcom = IntegerField()
    difflevel = IntegerField()
    class Meta:
        da_table = 'comcet4'

class Vocabulary(BaseModel):
    id = AutoField()
    uuid = UUIDField()
    word = CharField()
    ch_word = CharField()
    partofspeech = CharField()
    syllable = CharField()
    voiceid = CharField()
    frequency = FloatField()
    morph_size = FloatField()
    dispersion = FloatField()
    polysemy = FloatField()
    concre = FloatField()
    word_len = IntegerField()
    sylla_len = IntegerField()
    cet_level = CharField()
    fail_coe = FloatField()

    class Meta:
        db_table = 'vocabulary'

class Segment(BaseModel):
    id = AutoField()
    uuid = UUIDField()
    sentences_sequ = CharField()
    sent_lens = IntegerField()
    difficult_factor = FloatField()
    category_source = CharField()
    class Meta:
        db_table = 'segment'

class Sentence(BaseModel):
    id = AutoField()
    uuid = UUIDField()
    voca_sequ = CharField()
    voca_length = IntegerField()
    structure_type = IntegerField()
    part_sequ = CharField()
    sent_content = CharField()
    sent_voic_id = CharField()
    class Meta:
        db_table = 'sentence'

class VocabularyExtend(BaseModel):
    id = AutoField()
    basename = CharField()
    baseuuid = UUIDField()
    forms = CharField()
    speakvoiceids = CharField()
    class Meta:
        db_table = 'vocabularyextend'