import re
import urllib
from http.client import HTTPException
from lxml import etree
from urllib.error import HTTPError
from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qs

import nltk
import peewee
import syllables
import time

from caputer import Capture
from database.wordentity import Segment,Sentence,Vocabulary

class VocaModel:
    def __init__(self,word,cet_level=None,dest=None,vocadata=None):
        self.capture = Capture()
        self.cet_level ='0'  if cet_level is None  else cet_level
        self.dest_directory = '/root/baidupan_selenium/uterance/' if dest is None  else dest
        self.word = word.lower()
        self.vocaData = vocadata
        self.ch_word = '' if vocadata is None else vocadata.ch_word
        self.pos='' if vocadata is None else vocadata.partofspeech
        self.syllas='' if vocadata is None else vocadata.syllable
        self.voice='' if vocadata is None else vocadata.voiceid
        # 间隔时间
        self.intersec = 10
        self.do_init()


    @staticmethod
    def match_token(raw):
        result = re.match(r'\W*', raw)
        return result

    @classmethod
    def build_from_id(cls,id):
        vocaData = Vocabulary.get_or_none(Vocabulary.id == id)
        vocamodel = VocaModel(vocaData.word,vocaData.cet_level,None,vocaData)
        return vocamodel

    def build_word_token(self):
        print('标点' + self.word)
        self.vocaData = Vocabulary()
        # 直接存到单词表里,标记为标点符号
        self.vocaData.word = self.word
        self.vocaData.ch_word = self.word
        self.vocaData.partofspeech = 'token'
        self.vocaData.syllable = ''
        self.vocaData.voiceid = ''
        self.vocaData.word_len = 1
        self.vocaData.sylla_len = 1
        self.vocaData.cet_level = '0'

    def build_word(self):
        print('单词' + self.word)
        self.vocaData = Vocabulary()
        self.get_word()
        self.vocaData.word = self.word
        self.vocaData.ch_word = self.ch_word
        self.vocaData.partofspeech = self.pos
        self.vocaData.syllable = self.syllas
        self.vocaData.voiceid = self.voice
        self.vocaData.word_len = len(self.vocaData.word)
        self.vocaData.sylla_len = syllables.estimate(self.vocaData.word)
        self.vocaData.cet_level = self.cet_level

    # 初始化构建 peewee 对象为主的对象
    def do_init(self):
        # 如果是从 id 获取，则不需要做下面
        if self.vocaData is None:
            result = Vocabulary.get_or_none(Vocabulary.word == self.word)
            # 单词没有找到
            if result is None:
                self.capture.ontrigger(self)
                matchtoken = VocaModel.match_token(self.word)
                # 如果是标点，其他情况
                if matchtoken and matchtoken.group(0) == self.word:
                    self.build_word_token()
                # 单词找到
                else:
                    self.build_word()
                # 数据库存起来
                try:
                    self.vocaData.save()
                except peewee.IntegrityError:
                    print('存入失败')
            else:
                self.vocaData = result

    # 返回汉意、词性、音节、声音文件
    def get_word(self):
        pagehtml = self.get_page()
        html_content = etree.HTML(pagehtml.decode('utf-8'))
        self.ch_word, self.pos = self.get_ch_words(html_content)
        self.syllas, self.voice = self.get_speech(html_content)

    # 获取结果页面
    def get_page(self):
        basurl = 'http://cn.bing.com/dict/search?q='
        searchurl = basurl + self.word
        searchurl = Vocabulary.urlEncodeNonAscii(searchurl)
        # 获取响应
        try:
            response = urllib.request.urlopen(searchurl)
            html = response.read()
            return html
        except HTTPException | HTTPError:
            time.sleep(self.intersec)
            self.get_word()

    # 获取读音
    def get_speech(self,html_content):
        yingbiao_xpath = '/html/body/div[1]/div/div/div[1]/div[1]/div[1]/div[2]/div'
        speech_path = '(https\:.*?mp3)'
        reobj1 = re.compile(speech_path, re.I | re.M | re.S)
        get_yingbiao = html_content.xpath(yingbiao_xpath)
        for item in get_yingbiao:
            it = item.xpath('div')
            if len(it) > 0:
                # 处理没有读音或者音标的部分
                if len(it) > 1 and len(it[1].xpath('a')) > 1:
                    ddd = reobj1.findall(it[1].xpath('a')[0].get('onmouseover', None))
                    voicepath = re.compile('.*/([^/]*)')
                    matchresult = voicepath.match(ddd[0])
                    urllib.request.urlretrieve(ddd[0], self.dest_directory + matchresult[1])
                    return it[0].text[2:-1], matchresult[1]
                else:
                    return '', ''
        # 如果没有则返回两个空
            return '', ''

    # 获取中文释义
    def get_ch_words(self,html_content):
        ch_words = []
        poss = []
        ch_xpath = '/html/body/div[1]/div/div/div[1]/div[1]/ul/li'
        get_ch = html_content.xpath(ch_xpath)
        # 每一个
        for item in get_ch:
            span = item.xpath('span')
            poss.append(span[0].text)
            ch_words.append(span[1].xpath('span')[0].text)
        ch_word = ','.join(ch_words)
        pos = ','.join(poss)
        # 返回中文和词性
        return ch_word, pos

    # 进行解析
    @staticmethod
    def urlEncodeNonAscii(asc_url):
        s, n, p, q, f = urlsplit(asc_url)
        u_url = urlunsplit((s, n, p, urlencode(parse_qs(q), doseq=True), f))
        return u_url

    # 频率加一
    def frequency_add_one(self):
        self.vocaData.frequency += 1
        self.vocaData.save()
        print(self.vocaData.word+' '+str(self.vocaData.frequency))

class SentModel:
    def __init__(self,raw,sentdata=None):
        # 辅助用局部变量
        voca_sequ = []
        part_sequ = []
        if sentdata is not None:
            part_sequ = sentdata.part_sequ.split(',')
            voca_ids =  sentdata.voca_sequ.split(',')
            for voca_id in voca_ids:
                vocamodel = VocaModel.build_from_id(voca_id)
                # 单词组成的列表
                voca_sequ.append(vocamodel.word)
        self.capture = Capture()
        self.raw=raw
        self.sentData = sentdata
        self.tknzr = nltk.TweetTokenizer()
        self.voca_sequ = [] if sentdata is None else voca_sequ
        self.part_sequ = [] if sentdata is None else part_sequ

        self.do_init()

    def do_init(self):
        if self.sentData is None:
            self.voca_sequ,self.part_sequ = self.to_vocabu(self.raw)
            self.build_sentence()

    @classmethod
    def build_from_id(cls,id):
        sentdata = Sentence.get_or_none(Sentence.id == id)
        voca_str = []
        voca_sequ = sentdata.voca_sequ.split(',')
        for voca_id in map(int,voca_sequ):
            wordstr = VocaModel.build_from_id(voca_id).word
            voca_str.append(wordstr)
        sent_str = ' '.join(voca_str)
        return SentModel(sent_str,sentdata)

    def build_sentence(self):
        voca_str = ','.join(map(str, self.voca_sequ))
        pos_str = ','.join(map(str,self.part_sequ))
        self.sentData = Sentence.get_or_none(Sentence.voca_sequ == voca_str)
        if self.sentData is None:
            self.capture.ontrigger(self)
            self.sentData = Sentence()
            self.sentData.voca_sequ = voca_str
            self.sentData.voca_length = len(self.voca_sequ)
            self.sentData.part_sequ = pos_str
            try:
                self.sentData.save()
            except peewee.IntegrityError:
                print('句子存储失败')
    # 转化为单词的列表
    def to_vocabu(self,rawcontent):

        voca_sequ = []
        part_sequ = []
        split_words_with_token = self.tknzr.tokenize(rawcontent)
        tagged = nltk.pos_tag(split_words_with_token)
        # 每一个单词
        for tag in tagged:
            # 小写
            word = VocaModel(tag[0],cet_level='5')
            voca_sequ.append(word.vocaData.id)
            part_sequ.append(tag[1])
        return voca_sequ,part_sequ
    # 更新文字内容
    def update_content(self):
        self.sentData.sent_content = self.raw
        self.sentData.save()

class SegmentModel:
    def __init__(self,rawcontent,segdata=None):
        sentSeq = []
        if segdata is not None:
            sentSeq = segdata.sentences_sequ.split(',')
        self.capture = Capture()
        self.rawContent = rawcontent
        self.segData = segdata
        self.sentSeq = [] if segdata is None else sentSeq
        self.do_init()

    def do_init(self):
        if self.segData is None:
            self.rawContent = self.pre_deal(self.rawContent)
            self.rawContent = self.trim_chinese(self.rawContent)
            self.rawContent = self.trim_singUpcase(self.rawContent)
            # print('段落处理后'+self.rawContent)
            self.sentSeq = self.toSentList(self.rawContent)
            self.build_segment()

    @classmethod
    def build_from_id(cls,id):
        segmentData = Segment.get_or_none(Segment.id == id)
        sent_strs = []
        sent_sequ = segmentData.sentences_sequ.split(',')
        for sent_id in map(int,sent_sequ):
            sent_str = SentModel.build_from_id(sent_id).raw
            sent_strs.append(sent_str)
        seg_str = ''.join(sent_strs)
        return SegmentModel(seg_str,segmentData)

    def pre_deal(self,raw):
        # 去除行尾换行
        rawed = raw.strip('\n')
        # print('段落原文' + rawed)
        return rawed

    def trim_chinese(self,rawstr):
        return re.sub(r'\([\u4e00-\u9fa5]*…?[\u4e00-\u9fa5]*\)\s?','',rawstr)
    def trim_singUpcase(self,rawstr):
        return re.sub(r'\[[A-Z]\]\s?','',rawstr)

    def toSentList(self,rawsegment):
        rawsents = nltk.sent_tokenize(rawsegment)
        sentseq = []
        for rawsent in rawsents:
            sent = SentModel(rawsent)
            sentseq.append(sent.sentData.id)
        return sentseq

    def build_segment(self):
        # 获取对应序列的段落
        sentseqstr = ', '.join(map(str, self.sentSeq))
        self.segData = Segment.get_or_none(Segment.sentences_sequ == sentseqstr)
        if self.segData is None:
            self.capture.ontrigger(self)
            self.segData = Segment()
            self.segData.sentences_sequ = sentseqstr
            self.segData.sent_lens = len(self.sentSeq)
            self.segData.difficult_factor = 0
            self.segData.category_source = ''
            try:
                self.segData.save()
            except peewee.IntegrityError:
                print('段落存储失败')

    # 根据段落,对句子里的内容进行修改
    def modify_sentence(self):
        for sentID in map(int,self.segData.sentences_sequ.split(',')):
            sentmodel = SentModel.build_from_id(sentID)
            sentmodel.part_sequ = sentmodel.part_sequ.strip('[]')
            sentmodel.save()

