# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import traceback
import ConfigParser
from xml.etree import ElementTree


class AutoChangeConfig(object):
    def __init__(self):
        self.modifypath = ''
        # Changing the local path to the current text path
        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        self.home = os.getcwd()

        # Set log config
        logfloder = '%s/LOG' % self.home
        if not os.path.exists(logfloder):
            os.mkdir(logfloder)
        logfile = '%s/AutoChangeConfigLOG%s.log' % \
                  (logfloder, time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        logging.basicConfig(filename=logfile, level=logging.DEBUG,
                            format='%(asctime)s %(name)s %(lineno)d %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d-%a %H:%M:%S', filemode='w')
        self.loggerchangeconfig = logging.getLogger('ChangeConfig')
        formatter = logging.Formatter('%(asctime)s %(name)s %(lineno)d %(levelname)s  %(message)s')
        logscr = logging.StreamHandler()
        logscr.setFormatter(formatter)
        self.loggerchangeconfig.addHandler(logscr)

        # Read xml
        self.xmlroot = ElementTree.parse('AutoChangeConfig.xml')

        # Initialization Delimiter
        self.delimiter = [':', '=', '》', '>', '-》', '->', '=>', '=》']

        # Initialization read ini
        self.conf = ConfigParser.ConfigParser()
        ConfigParser.optionsxform = str

    def readconfig(self):
        # Get path, suffix, and modify content from configuration file
        self.loggerchangeconfig.info('Begin Read Config xml')
        for modify_node in self.xmlroot.findall('./modify'):
            modify_file_path = modify_node.find('file').text
            modify_file_suffix = str(os.path.basename(modify_node.find('file').text)).split('.')[-1]
            self.dispatch(modify_file_suffix, modify_file_path, modify_node.findall('change'), modify_node)

    def dispatch(self, suffix, path, changed, modify_node):
        # Select different functions according to the suffix
        try:
            if 'xml' == suffix:
                self.modifyxml(path, changed)
            elif 'properties' == suffix:
                self.modifyproperties(path, changed)
            elif 'ini' == suffix:
                self.modifyini(path, changed, modify_node)
            elif 'cfg' == suffix:
                self.modifycfg(path, changed)
            else:
                self.loggerchangeconfig.error('There is no suffix matching, Please check the configuration file')
        except Exception, c:
            if c:
                self.loggerchangeconfig.error(traceback.format_exc())

    def modifyproperties(self, path, changed):
        self.loggerchangeconfig.info('Begin modify properties file')
        self.loggerchangeconfig.info('The modify properties file is \"%s\"' % path)
        self.modifyotherfile(path, changed)
        self.loggerchangeconfig.info('modify properties file \"%s\" done' % path)

    def modifyini(self, path, changed, modify_node):
        if modify_node.find('nodename') is not None:
            begin_num = 0
            n = 0
            begin_num_list = [0]
            end_num_list = []
            node_str = '[' + str(modify_node.find('nodename').text) + ']'
            self.loggerchangeconfig.info('Begin modify ini file')
            self.loggerchangeconfig.info('The modify ini file is \"%s\"' % path)
            with open(path, 'r') as f:
                cfg_content = f.read()
            while True:
                n += 1
                with open(path, 'r') as fr:
                    cfg_content2 = fr.read()
                if str(cfg_content2)[begin_num_list[-1]:].find(node_str) >= 0:
                    begin_num = int(str(cfg_content2)[begin_num_list[-1]:].find(node_str)) + len(node_str) + begin_num_list[-1]
                    begin_num_list.append(begin_num)
                    if -1 == str(cfg_content2[begin_num:]).find('['):
                        end_first_num = len(cfg_content2)
                    else:
                        end_first_num = str(cfg_content2[begin_num:]).find('[') + begin_num
                    end_num_list.append(end_first_num)
                    # print 'begin_num is %d' % begin_num
                    # print 'end_num: %d' % end_first_num
                    # print '----'
                    # print begin_num_list
                    # print '++++'
                    # print end_num_list
                    with open(path, 'w') as fw:
                        fw.write(cfg_content2.replace(cfg_content2[begin_num:end_first_num], '\nautochangeconfig%d\n' % n))

                else:
                    break

            while True:
                if str(cfg_content)[begin_num_list[-1]:].find(node_str) >= 0:
                    begin_num = int(str(cfg_content)[begin_num_list[-1]:].find(node_str)) + len(node_str) + begin_num_list[-1]
                    begin_num_list.append(begin_num)
                    if -1 == str(cfg_content[begin_num:]).find('['):
                        end_first_num = len(cfg_content)
                    else:
                        end_first_num = str(cfg_content[begin_num:]).find('[') + begin_num
                    end_num_list.append(end_first_num)
                    # print 'begin_num is %d' % begin_num
                    # print 'end_num: %d' % end_first_num
                    # print '----'
                    # print begin_num_list
                    # print '++++'
                    # print end_num_list
                    print str(cfg_content[begin_num:end_first_num])

                else:
                    break

            # del(begin_num_list[0])
            # for i in range(0, len(begin_num_list)):
            #     with open(path, 'r') as fr:
            #         cfg_content3 = fr.read()
            #     tmpfile_path = os.path.join(self.home, 'temp')
            #     with open(tmpfile_path, 'w') as fw:
            #         fw.write(str(cfg_content[begin_num_list[i]:end_num_list[i]]))
            #     self.modifyotherfile(tmpfile_path, changed)
            #     with open(tmpfile_path, 'r') as fr:
            #         fr_str = fr.read()
            #     # print fr_str
            #     with open(path, 'w') as fw:
            #         fw.write(str(cfg_content3).replace('autochangeconfig%d' % (i + 1), fr_str))
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
        self.loggerchangeconfig.info(changed)

    def modifyotherfile(self, path, changed):
        cfg_content_new = ''
        with open(path, 'r') as f:
            cfg_content = f.readlines()
        for change_str in changed:
            if '' != cfg_content_new:
                cfg_content = cfg_content_new
            # print '--->' + str(cfg_content) + '<---'
            cfg_content_new = self.replacestring(change_str.text, cfg_content)

        # print '++++' + str(cfg_content_new) + '++++'
        with open(path, 'w') as f2:
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
                    for i in range(0, len(originalcontent)):
                        # Look for a similar string in each line
                        begin_num = str(originalcontent[i]).find(str(replacestr).split(symbol)[0] + symbol)
                        if begin_num >= 0:
                            # print '>>>' + str(symbol) + '<<<'
                            # print '>>>' + str(begin_num) + '<<<'
                            # print '>>>' + str(replacestr) + '<<<'
                            originalcontent[i] = str(replacestr) + '\n'
                            find_key = 'true'
                    if 'false' == find_key:
                        # print '>>>' + str(replacestr) + '<<<'
                        # print originalcontent
                        originalcontent.append('\n' + str(replacestr))
                    find_separator = 'true'
                if 'true' == find_separator:
                    break
            except Exception, d:
                if d:
                    pass
        return originalcontent

    def main(self):
        try:
            command1 = sys.argv[1]
            if 'help' == command1 or '-help' == command1 or '--help' == command1 or '?' == command1 or '/?' == command1:
                self.loggerchangeconfig.info('print help')
                print 'Please modify the configuration file as needed\n'
                sys.exit()
            else:
                self.readconfig()
        except Exception, b:
            if b:
                self.readconfig()


if __name__ == '__main__':
    a = AutoChangeConfig()
    a.main()
