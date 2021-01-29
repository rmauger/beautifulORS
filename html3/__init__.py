'''Version History (in Brief)
--------------------------

- 1.18 Fixed support of python 3.8
- 1.17 First release of html3
- 1.16 detect and raise a more useful error when some WSGI frameworks
  attempt to call HTML.read(). Also added ability to add new content using
  the += operator.
- 1.15 fix Python 3 compatibility (unit tests)
- 1.14 added plain XML support
- 1.13 allow adding (X)HTML instances (tags) as new document content
- 1.12 fix handling of XHTML empty tags when generating unicode
  output (thanks Carsten Eggers)
- 1.11 remove setuptools dependency
- 1.10 support plain ol' distutils again
- 1.9 added unicode support for Python 2.x
- 1.8 added Python 3 compatibility
- 1.7 added Python 2.5 compatibility and escape argument to tag
  construction
- 1.6 added .raw_text() and and WSGI compatibility
- 1.5 added XHTML support
- 1.3 added more documentation, more tests
- 1.2 added special-case klass / class attribute
- 1.1 added escaping control
- 1.0 was the initial release

----

I would be interested to know whether this module is useful - if you use it
please indicate so at https://www.ohloh.net/p/pyhtml

This code is copyright 2009-2011 eKit.com Inc (http://www.ekit.com/)
See the end of the source file for the license of use.
XHTML support was contributed by Michael Haubenwallner.'''

# from __future__ import with_statement
# __version__ = '1.18'

import sys
import html
import unittest


class HTML(object):
    newline_default_on = set('table ol ul dl'.split())

    def __init__(self, name=None, text=None, stack=None, newlines=True,
            escape=True):
        self._name = name
        self._content = []
        self._attrs = {}
        # insert newlines between content?
        if stack is None:
            stack = [self]
            self._top = True
            self._newlines = newlines
        else:
            self._top = False
            self._newlines = name in self.newline_default_on
        self._stack = stack
        if text is not None:
            self.text(text, escape)

    def __getattr__(self, name):
        # adding a new tag or newline
        if name == 'newline':
            e = '\n'
        else:
            e = self.__class__(name, stack=self._stack)
        if self._top:
            self._stack[-1]._content.append(e)
        else:
            self._content.append(e)
        return e

    def __iadd__(self, other):
        if self._top:
            self._stack[-1]._content.append(other)
        else:
            self._content.append(other)
        return self

    def text(self, text, escape=True):
        """Add text to the document. If "escape" is True any characters
        special to HTML will be escaped.
        """
        if escape:
            text = html.escape(text)
        # adding text
        if self._top:
            self._stack[-1]._content.append(text)
        else:
            self._content.append(text)

    def raw_text(self, text):
        """Add raw, unescaped text to the document. This is useful for
        explicitly adding HTML code or entities.
        """
        return self.text(text, escape=False)

    def __call__(self, *content, **kw):
        if self._name == 'read':
            if len(content) == 1 and isinstance(content[0], int):
                raise TypeError('you appear to be calling read(%d) on '
                    'a HTML instance' % content)
            elif len(content) == 0:
                raise TypeError('you appear to be calling read() on a '
                    'HTML instance')

        # customising a tag with content or attributes
        escape = kw.pop('escape', True)
        if content:
            if escape:
                self._content = list(map(html.escape, content))
            else:
                self._content = content
        if 'newlines' in kw:
            # special-case to allow control over newlines
            self._newlines = kw.pop('newlines')
        for k in kw:
            if k == 'klass':
                self._attrs['class'] = html.escape(kw[k], True)
            else:
                self._attrs[k] = html.escape(kw[k], True)
        return self

    def __enter__(self):
        # we're now adding tags to me!
        self._stack.append(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # we're done adding tags to me!
        self._stack.pop()

    def __repr__(self):
        return '<HTML %s 0x%x>' % (self._name, id(self))

    def _stringify(self, str_type):
        # turn me and my content into text
        join = '\n' if self._newlines else ''
        if self._name is None:
            return join.join(map(str_type, self._content))
        a = ['%s="%s"' % i for i in self._attrs.items()]
        l = [self._name] + a
        s = '<%s>%s' % (' '.join(l), join)
        if self._content:
            s += join.join(map(str_type, self._content))
            s += join + '</%s>' % self._name
        return s

    def __str__(self):
        return self._stringify(str)

    def __iter__(self):
        return iter([str(self)])

''' def __unicode__(self):
        return self._stringify(unicode)
'''

class XHTML(HTML):
    """Easily generate XHTML.
    """
    empty_elements = set('base meta link hr br param img area input col \
        colgroup basefont isindex frame'.split())

    def _stringify(self, str_type):
        # turn me and my content into text
        # honor empty and non-empty elements
        join = '\n' if self._newlines else ''
        if self._name is None:
            return join.join(map(str_type, self._content))
        a = ['%s="%s"' % i for i in self._attrs.items()]
        l = [self._name] + a
        s = '<%s>%s' % (' '.join(l), join)
        if self._content or not(self._name.lower() in self.empty_elements):
            s += join.join(map(str_type, self._content))
            s += join + '</%s>' % self._name
        else:
            s = '<%s />%s' % (' '.join(l), join)
        return s


class XML(XHTML):
    """Easily generate XML.

    All tags with no contents are reduced to self-terminating tags.
    """
    newline_default_on = set()          # no tags are special

    def _stringify(self, str_type):
        # turn me and my content into text
        # honor empty and non-empty elements
        join = '\n' if self._newlines else ''
        if self._name is None:
            return join.join(map(str_type, self._content))
        a = ['%s="%s"' % i for i in self._attrs.items()]
        l = [self._name] + a
        s = '<%s>%s' % (' '.join(l), join)
        if self._content:
            s += join.join(map(str_type, self._content))
            s += join + '</%s>' % self._name
        else:
            s = '<%s />%s' % (' '.join(l), join)
        return s


class TestCase(unittest.TestCase):
    def test_empty_tag(self):
        """generation of an empty HTML tag"""
        self.assertEquals(str(HTML().br), '<br>')

    def test_empty_tag_xml(self):
        """generation of an empty XHTML tag"""
        self.assertEquals(str(XHTML().br), '<br />')

    def test_tag_add(self):
        """test top-level tag creation"""
        self.assertEquals(str(HTML('html', 'text')), '<html>\ntext\n</html>')

    def test_tag_add_no_newline(self):
        """test top-level tag creation"""
        self.assertEquals(str(HTML('html', 'text', newlines=False)),
            '<html>text</html>')

    def test_iadd_tag(self):
        """test iadd'ing a tag"""
        h = XML('xml')
        h += XML('some-tag', 'spam', newlines=False)
        h += XML('text', 'spam', newlines=False)
        self.assertEquals(str(h),
            '<xml>\n<some-tag>spam</some-tag>\n<text>spam</text>\n</xml>')

    def test_iadd_text(self):
        """test iadd'ing text"""
        h = HTML('html', newlines=False)
        h += 'text'
        h += 'text'
        self.assertEquals(str(h), '<html>texttext</html>')

    def test_xhtml_match_tag(self):
        """check forced generation of matching tag when empty"""
        self.assertEquals(str(XHTML().p), '<p></p>')

    def test_just_tag(self):
        """generate HTML for just one tag"""
        self.assertEquals(str(HTML().br), '<br>')

    def test_just_tag_xhtml(self):
        """generate XHTML for just one tag"""
        self.assertEquals(str(XHTML().br), '<br />')

    def test_xml(self):
        """generate XML"""
        self.assertEquals(str(XML().br), '<br />')
        self.assertEquals(str(XML().p), '<p />')
        self.assertEquals(str(XML().br('text')), '<br>text</br>')

    def test_para_tag(self):
        """generation of a tag with contents"""
        h = HTML()
        h.p('hello')
        self.assertEquals(str(h), '<p>hello</p>')

    def test_escape(self):
        """escaping of special HTML characters in text"""
        h = HTML()
        h.text('<>&')
        self.assertEquals(str(h), '&lt;&gt;&amp;')

    def test_no_escape(self):
        """no escaping of special HTML characters in text"""
        h = HTML()
        h.text('<>&', False)
        self.assertEquals(str(h), '<>&')

    def test_escape_attr(self):
        """escaping of special HTML characters in attributes"""
        h = HTML()
        h.br(id='<>&"')
        self.assertEquals(str(h), '<br id="&lt;&gt;&amp;&quot;">')

    def test_subtag_context(self):
        """generation of sub-tags using "with" context"""
        h = HTML()
        with h.ol:
            h.li('foo')
            h.li('bar')
        self.assertEquals(str(h), '<ol>\n<li>foo</li>\n<li>bar</li>\n</ol>')

    def test_subtag_direct(self):
        """generation of sub-tags directly on the parent tag"""
        h = HTML()
        l = h.ol
        l.li('foo')
        l.li.b('bar')
        self.assertEquals(str(h),
            '<ol>\n<li>foo</li>\n<li><b>bar</b></li>\n</ol>')

    def test_subtag_direct_context(self):
        """generation of sub-tags directly on the parent tag in "with" context"""
        h = HTML()
        with h.ol as l:
            l.li('foo')
            l.li.b('bar')
        self.assertEquals(str(h),
            '<ol>\n<li>foo</li>\n<li><b>bar</b></li>\n</ol>')

    def test_subtag_no_newlines(self):
        """prevent generation of newlines against default"""
        h = HTML()
        l = h.ol(newlines=False)
        l.li('foo')
        l.li('bar')
        self.assertEquals(str(h), '<ol><li>foo</li><li>bar</li></ol>')

    def test_add_text(self):
        """add text to a tag"""
        h = HTML()
        p = h.p('hello, world!\n')
        p.text('more text')
        self.assertEquals(str(h), '<p>hello, world!\nmore text</p>')

    def test_add_text_newlines(self):
        """add text to a tag with newlines for prettiness"""
        h = HTML()
        p = h.p('hello, world!', newlines=True)
        p.text('more text')
        self.assertEquals(str(h), '<p>\nhello, world!\nmore text\n</p>')

    def test_doc_newlines(self):
        """default document adding newlines between tags"""
        h = HTML()
        h.br
        h.br
        self.assertEquals(str(h), '<br>\n<br>')

    def test_doc_no_newlines(self):
        """prevent document adding newlines between tags"""
        h = HTML(newlines=False)
        h.br
        h.br
        self.assertEquals(str(h), '<br><br>')

    def test_table(self):
        """multiple "with" context blocks"""
        h = HTML()
        with h.table(border='1'):
            for _ in range(2):
                with h.tr:
                    h.td('column 1')
                    h.td('column 2')
        self.assertEquals(str(h),)

if __name__ == '__main__':
    unittest.main()


# Copyright (c) 2009 eKit.com Inc (http://www.ekit.com/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# vim: set filetype=python ts=4 sw=4 et si