# !/usr/local/python
# -*- coding: UTF-8 -*-
import os
import shutil
import sys
import time
import logging
import traceback
import ConfigParser
from xml.etree import ElementTree


class AutoChangeConfig(object):
    def __init__(self):
        self.modifypath = ''
        self.xml_notes_list = []
        self.other_notes_list = []
        self.ini_notes_list = []
        self.ini_notes_tmp_list = []
        self.config_file = 'AutoChangeConfig.xml'
        # Changing the local path to the current text path
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        self.home = os.getcwd()

        # Set log config
        logfloder = '%s/LOG' % self.home
        self.time_now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if not os.path.exists(logfloder):
            os.mkdir(logfloder)
        logfile = '%s/AutoChangeConfigLOG%s.log' % \
                  (logfloder, self.time_now)
        logging.basicConfig(filename=logfile, level=logging.DEBUG,
                            format='%(asctime)s %(name)s %(lineno)d %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d-%a %H:%M:%S', filemode='wb')
        self.loggerchangeconfig = logging.getLogger('ChangeConfig')
        formatter = logging.Formatter('%(asctime)s %(name)s %(lineno)d %(levelname)s  %(message)s')
        logscr = logging.StreamHandler()
        logscr.setFormatter(formatter)
        self.loggerchangeconfig.addHandler(logscr)

        # Read xml
        self.xmlroot = ElementTree.parse(self.config_file)

        # Initialization Delimiter
        self.delimiter = [':', '=', '》', '>', '-》', '->', '=>', '=》']

        # Initialization read ini
        self.conf = ConfigParser.ConfigParser()
        ConfigParser.optionsxform = str

        # Initialization backup floder path
        self.backupfloder = os.path.join(self.home, 'BackUp')

    def readconfig(self):
        # Get path, suffix, and modify content from configuration file
        self.loggerchangeconfig.info('Begin Read Config xml')
        self.loggerchangeconfig.info('Config xml now is %s' % str(self.config_file))
        for modify_node in self.xmlroot.findall('./modify'):
            modify_file_path = modify_node.find('file').text
            modify_file_suffix = str(os.path.basename(modify_node.find('file').text)).split('.')[-1]
            self.backupconfig(modify_file_path)
            self.dispatch(modify_file_suffix, modify_file_path, modify_node.findall('change'), modify_node)

        # Backup AutoChangeConfig config file
        auto_cfg_file = os.path.join(self.home, self.config_file)
        self.backupconfig(auto_cfg_file)

    def dispatch(self, suffix, path, changed, modify_node):
        # Select different functions according to the suffix
        try:
            if 'xml' == suffix:
                self.lookupannotations(path, suffix)
                self.modifyxml(path, changed)
            elif 'properties' == suffix:
                self.lookupannotations(path, suffix)
                self.modifyproperties(path, changed)
            elif 'ini' == suffix:
                self.lookupannotations(path, suffix)
                self.ini_notes_tmp_list = self.ini_notes_list
                self.modifyini(path, changed, modify_node)
            elif 'cfg' == suffix:
                self.lookupannotations(path, suffix)
                self.modifycfg(path, changed)
            else:
                self.loggerchangeconfig.error('There is no suffix matching, Please check the configuration file')
        except Exception, dispatch_err:
            if dispatch_err:
                self.loggerchangeconfig.error(traceback.format_exc())

    def modifyproperties(self, path, changed):
        self.loggerchangeconfig.info('Begin modify properties file')
        self.loggerchangeconfig.info('The modify properties file is \"%s\"' % path)
        self.modifyotherfile(path, changed)
        self.loggerchangeconfig.info('modify properties file \"%s\" done' % path)

    def modifyini(self, path, changed, modify_node):
        if modify_node.find('nodename') is not None:
            n = 0
            begin_num_list_tmp = [0]
            end_num_list = []
            node_str = '[' + str(modify_node.find('nodename').text) + ']'
            self.loggerchangeconfig.info('Begin modify ini file')
            self.loggerchangeconfig.info('The modify ini file is \"%s\"' % path)
            with open(path, 'rb') as f:
                cfg_content = f.read()
            while True:
                n += 1
                self.lookupannotations(path, 'ini')
                with open(path, 'rb') as fr:
                    cfg_content2 = fr.read()
                if str(cfg_content2)[begin_num_list_tmp[-1]:].find(node_str) >= 0:
                    begin_num = int(str(cfg_content2)[begin_num_list_tmp[-1]:].find(node_str)) + len(node_str) + \
                                begin_num_list_tmp[-1]
                    begin_num_list_tmp.append(begin_num)
                    if -1 == str(cfg_content2[begin_num:]).find('['):
                        end_num = len(cfg_content2)
                    else:
                        end_num = str(cfg_content2[begin_num:]).find('[') + begin_num - 1
                    # print 'begin_num is %d' % begin_num
                    # print 'end_num: %d' % end_first_num
                    # print '----'
                    # print begin_num_list
                    # print '++++'
                    # print end_num_list
                    with open(path, 'wb') as fw:
                        if not 'false' == self.judgerange(begin_num, self.ini_notes_list):
                            fw.write(cfg_content2.replace(cfg_content2[begin_num:end_num],
                                                          '\nautochangeconfig%d\n' % n))
                        else:
                            fw.write(cfg_content2)

                else:
                    break

            begin_num_list = [0]
            while True:
                if str(cfg_content)[begin_num_list[-1]:].find(node_str) >= 0:
                    begin_num = int(str(cfg_content)[begin_num_list[-1]:].
                                    find(node_str)) + len(node_str) + begin_num_list[-1]
                    begin_num_list.append(begin_num)
                    if -1 == str(cfg_content[begin_num:]).find('['):
                        end_num = len(cfg_content)
                    else:
                        end_num = str(cfg_content[begin_num:]).find('[') + begin_num
                    end_num_list.append(end_num)
                    # print 'begin_num is %d' % begin_num
                    # print 'end_num: %d' % end_first_num
                    # print '----'
                    # print begin_num_list
                    # print '++++'
                    # print end_num_list
                    # print str(cfg_content[begin_num:end_num])

                else:
                    break

            del(begin_num_list[0])
            for i in range(0, len(begin_num_list)):
                if not 'false' == self.judgerange(begin_num_list[i], self.ini_notes_tmp_list):
                    with open(path, 'rb') as fr:
                        cfg_content3 = fr.read()
                    tmpfile_path = os.path.join(self.home, 'temp')
                    with open(tmpfile_path, 'wb') as fw:
                        # print str(cfg_content[begin_num_list[i]:end_num_list[i]])
                        fw.write(str(cfg_content[begin_num_list[i]:end_num_list[i]-1]))
                    self.lookupannotations(tmpfile_path, 'other')
                    self.modifyotherfile(tmpfile_path, changed)
                    with open(tmpfile_path, 'rb') as fr:
                        fr_str = fr.read()
                    # print fr_str
                    with open(path, 'wb') as fw:
                        fw.write(str(cfg_content3).replace('\nautochangeconfig%d\n' % (i + 1), fr_str))
                    os.remove(tmpfile_path)
            self.loggerchangeconfig.info('modify ini file \"%s\" done' % path)
        else:
            self.loggerchangeconfig.info('Begin modify ini file')
            self.loggerchangeconfig.info('The modify ini file is \"%s\"' % path)
            self.modifyotherfile(path, changed)
            self.loggerchangeconfig.info('modify ini file \"%s\" done' % path)

    def modifycfg(self, path, changed):
        self.loggerchangeconfig.info('Begin modify cfg file')
        self.loggerchangeconfig.info('The modify cfg file is \"%s\"' % path)
        self.modifyotherfile(path, changed)
        self.loggerchangeconfig.info('modify cfg file \"%s\" done' % path)

    def modifyxml(self, path, changed):
        self.loggerchangeconfig.info('Begin modify xml file')
        self.loggerchangeconfig.info('The modify xml file is \"%s\"' % path)
        for change_str in changed:
            # Read the original text by line and get the list of text.
            with open(path, 'rb') as fr:
                b_list = fr.readlines()
            changed_list = []
            original_list = []
            number_list = []
            first_line_num_list = []
            previous_line_num = 0
            try:
                change_str.text = change_str.text.encode('utf-8')
            except Exception, xml_err:
                if xml_err:
                    change_str.text = change_str.text
            # Remove the tab to modify the content and cut it by line.
            a_list = str(change_str.text).replace('\t', '').splitlines()
            for a_list_str in a_list:
                if '' != a_list_str:
                    # Remove the empty line
                    changed_list.append(a_list_str)
            for b_list_str in b_list:
                if '' != b_list_str:
                    # Remove the empty line\tab
                    original_list.append(b_list_str.replace('\t', '').replace('\n', '').lstrip().rstrip())
            for l in range(0, len(original_list)):
                if str(original_list[l]) == str(changed_list[0]):
                    # Lists all rows that modify the contents of the first row in the original article.
                    if not 'false' == self.judgerange(l, self.xml_notes_list):
                        first_line_num_list.append(l)
            changed_list_lines = len(changed_list)
            for i in range(0, changed_list_lines):
                try:
                    # List all the lines that modify the content in the original article.
                    previous_line_num += original_list[previous_line_num:].index(changed_list[i])
                    if not 'false' == self.judgerange(previous_line_num, self.xml_notes_list):
                        number_list.append(previous_line_num)
                except Exception, xml_err:
                    if xml_err:
                        pass

            # List the first lines that are really modified in the original text
            last_first_line = self.getlinenumber(number_list, first_line_num_list)
            # if -1 == last_first_line:
            #     self.loggerchangeconfig.error('Can\'t find content, please check your configuration')
            #     return

            with open(path, 'rb') as fr:
                c_list = fr.readlines()

            lastchange_list = str(change_str.text).splitlines(True)
            for m in range(0, len(lastchange_list)):
                # Modify the corresponding content in the original text
                if m == len(lastchange_list) - 1:
                    lastchange_list[m] += '\r\n'
                c_list[last_first_line+m] = lastchange_list[m]

            with open(path, 'wb') as fw:
                fw.writelines(c_list)
        self.loggerchangeconfig.info('Modify xml file done.')

    def modifyotherfile(self, path, changed):
        cfg_content_new = ''
        with open(path, 'rb') as f:
            cfg_content = f.readlines()
        for change_str in changed:
            if '' != cfg_content_new:
                cfg_content = cfg_content_new
            # print '--->' + str(cfg_content) + '<---'
            cfg_content_new = self.replacestring(change_str.text, cfg_content)

        # print '++++' + str(cfg_content_new) + '++++'
        with open(path, 'wb') as f2:
            for line in cfg_content_new:
                f2.write(line)

    def replacestring(self, replacestr, originalcontent):
        """
        Find in the article whether there is a row that is similar to the string to replace,
        and if so, replace the line with that string
        :param replacestr: A string to replace
        :param originalcontent: A list of the whole articles read by line
        :return: A list of articles read by line after the replacement
        """
        find_separator = ''
        # Cut the string to be replaced by a special character
        for symbol in self.delimiter:
            find_key = 'false'
            try:
                if str(replacestr).split(symbol)[1]:
                    self.loggerchangeconfig.info('Now modify %s' % str(str(replacestr).split(symbol)[0]))
                    for i in range(0, len(originalcontent)):
                        # Look for a similar string in each line
                        if not 'false' == self.judgerange(i, self.other_notes_list):
                            begin_num = str(originalcontent[i]).find(str(replacestr).split(symbol)[0] + symbol)
                            if begin_num == 0:
                                # print '>>>' + str(symbol) + '<<<'
                                # print '>>>' + str(begin_num) + '<<<'
                                # print '>>>' + str(replacestr) + '<<<'
                                originalcontent[i] = str(replacestr) + '\n'
                                find_key = 'true'
                    if 'false' == find_key:
                        # print '>>>' + str(replacestr) + '<<<'
                        # print originalcontent
                        self.loggerchangeconfig.info('Now add %s' % str(replacestr))
                        originalcontent.append('\n' + str(replacestr))
                    find_separator = 'true'
                if 'true' == find_separator:
                    break
            except Exception, replace_err:
                if replace_err:
                    pass
        return originalcontent

    def getlinenumber(self, num_list, first_line_num_list):
        d_value1 = 0
        last_first_num = 0
        # print num_list
        # print first_line_num_list
        for num in first_line_num_list:
            if num <= num_list[-1]:
                d_value2 = int(num_list[-1]) - int(num)
                if d_value2 < d_value1:
                    last_first_num = num
                elif 0 == int(last_first_num):
                    last_first_num = num
                d_value1 = d_value2
        self.loggerchangeconfig.info('Modify xml\'s first line number is %d' % int(last_first_num))
        return last_first_num

    def backupconfig(self, path):
        n = 0
        backupfloder = self.backupfloder
        self.loggerchangeconfig.info('Begin Backup \"%s\"' % path)
        # Create backup floder
        if not os.path.exists(backupfloder):
            os.mkdir(backupfloder)

        backupfloder_now = os.path.join(backupfloder, '%s' % self.time_now)

        # Create backup Subfolder
        if not os.path.exists(backupfloder_now):
            os.mkdir(backupfloder_now)

        while True:
            backupfloder_now_new = os.path.join(backupfloder_now, 'backup%d' % n)
            if not os.path.exists(backupfloder_now_new):
                os.mkdir(backupfloder_now_new)
                break
            else:
                n += 1

        # Backup config file
        if os.path.exists(path):
            backupfile_path = os.path.join(backupfloder_now_new, os.path.basename(path))
            shutil.copyfile(path, backupfile_path)
            backup_path_path = os.path.join(backupfloder_now_new, 'path')
            with open(backup_path_path, 'wb') as fw:
                try:
                    # fw.write(path)
                    fw.write(path.encode('utf-8'))
                except Exception, backup_err:
                    if backup_err:
                        fw.write(path)

        self.loggerchangeconfig.info('Backup \"%s\" done' % path)

    def restorebackup(self, timestamp):
        backupfloder_restore = os.path.join(self.backupfloder, '%s' % timestamp)
        if not os.path.exists(backupfloder_restore):
            self.loggerchangeconfig.error('Can\'t find backup floder, please check your time stamp')
            return

        # restore the backup file
        for p in range(0, len(os.listdir(backupfloder_restore))):
            backup_file_path = os.path.join(backupfloder_restore, 'backup%d' % p)
            with open(os.path.join(backup_file_path, 'path'), 'rb') as fr:
                restore_path = fr.read()
            try:
                if 'AutoChangeConfig.xml' == os.path.basename(restore_path):
                    continue
                self.loggerchangeconfig.info('Now restore \"%s\"' % restore_path)
                shutil.copyfile(os.path.join(backup_file_path,
                                             os.path.basename(restore_path)), restore_path.decode('utf-8'))
            except Exception, restore_err:
                if restore_err:
                    self.loggerchangeconfig.error(traceback.format_exc())
        self.loggerchangeconfig.info('Restore config file done')

    def lookupannotations(self, path, suffix):
        with open(path, 'rb') as fr:
            notes_str = fr.readlines()
        if 'xml' == suffix:
            c_list = []
            d_list = []
            for n in range(0, len(notes_str)):
                if str(notes_str[n]).find('<!--') >= 0:
                    d_list.append(n)
                if str(notes_str[n]).find('-->') >= 0:
                    d_list.append(n)
                    c_list.append(d_list)
                    d_list = []
            # print c_list
            self.xml_notes_list = c_list
        elif 'ini' == suffix:
            with open(path, 'rb') as fr:
                ini_notes_str = fr.read()
            c_list = []
            d_list = []
            notes_end_num = 0
            while True:
                notes_begin_num = ini_notes_str[notes_end_num:].find('#')
                if notes_begin_num >= 0:
                    notes_begin_tmp_num = notes_begin_num + notes_end_num
                    d_list.append(notes_begin_tmp_num)
                    notes_end_num = ini_notes_str[notes_begin_tmp_num:].find('\n')
                    notes_end_tmp_num = notes_begin_tmp_num + notes_end_num
                    notes_end_num = notes_end_tmp_num
                    d_list.append(notes_end_tmp_num)
                    c_list.append(d_list)
                    d_list = []
                else:
                    break
            # print c_list
            self.ini_notes_list = c_list
        else:
            c_list = []
            d_list = []
            for n in range(0, len(notes_str)):
                if str(notes_str[n]).find('#') >= 0:
                    d_list.append(n)
                    d_list.append(n)
                    c_list.append(d_list)
                    d_list = []
            # print c_list
            self.other_notes_list = c_list

    @staticmethod
    def judgerange(num, lst):
        for o in range(0, len(lst)):
            if num >= lst[o][0]:
                if num <= lst[o][1]:
                    return 'false'

    def main(self):
        try:
            command1 = sys.argv[1]
            if 'help' == command1 or '-help' == command1 or '--help' == command1 or '?' == command1 or '/?' == command1:
                self.loggerchangeconfig.info('print help')
                self.loggerchangeconfig.info('Please modify the configuration file as needed\n')
                sys.exit()
            elif str(command1).isdigit():
                if 14 == len(command1):
                    self.restorebackup(command1)
                else:
                    self.loggerchangeconfig.info('The backup file name is error\n')
            elif str(command1).find('AutoChangeConfig') >= 0:
                if not os.path.exists(command1):
                    self.loggerchangeconfig.error('The path is not exists.')
                    return
                self.config_file = str(command1)
                self.xmlroot = ElementTree.parse(self.config_file)
                self.readconfig()
            else:
                self.loggerchangeconfig.error('The parameter is wrong.')
        except Exception, main_err:
            if main_err:
                self.readconfig()


if __name__ == '__main__':
    a = AutoChangeConfig()
    a.main()
