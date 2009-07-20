#
# enum.py -- Class to implement enumerated types.
#
# Copyright (c) 2008, Blakita Software, LLC
#
# Brian St. Pierre, <brian@bstpierre.org>
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written agreement
# is hereby granted, provided that the above copyright notice and this
# paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT,
# INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST
# PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS IS"
# BASIS, AND THE AUTHOR HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
# Change History
#  1 - 2008-12-14 - Written
#


'''This provides an enumerated type. Derive from Enumeration and set
_enum_ to a list of names. The type will have these names
available as attributes on the type.

>>> class EnumTest(Enumeration):
...     _enum_ = ['foo', 'bar', 'rab', 'oof']
...
>>> et = EnumTest()
>>> et2 = EnumTest()
>>> et == et2
True
>>> id(et) == id(et2)
True
>>> et.foo
<EnumTest: foo=0>
>>> et.foo == 0
True
>>> et.foo == 1 - 1
True
>>> et.foo + 1 == et.bar
True
>>> et.bar
<EnumTest: bar=1>
>>> 3 in et
True
>>> "blech" in et2
False
>>> "foo" in et
True
>>> EnumTest.foo
<EnumTest: foo=0>
>>> EnumTest.bar
<EnumTest: bar=1>
>>> EnumTest.rab
<EnumTest: rab=2>
>>> EnumTest.oof
<EnumTest: oof=3>
>>> EnumTest.oof.name
'oof'
>>> EnumTest.oof.name = 'foo'
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
    et.foo = 6
AttributeError: '_EnumerationValue' object attribute 'name' is read-only
>>> EnumTest.oof.name
'oof'
>>> 0 in EnumTest
True
>>> 4 in EnumTest
False
>>> et.zzz = 6
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
    et.zzz
AttributeError: 'EnumTest' object has no attribute 'zzz'
>>> et.foo = 6
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
    et.foo = 6
AttributeError: 'EnumTest' object attribute 'foo' is read-only
'''


class _EnumerationValue(int):
    '''Enumeration values are integers with a "name" property.'''
    __slots__ = ['name', '_enum']

    def __new__(cls, name, enum_name, *args, **kwargs):
        instance = int.__new__(cls, *args, **kwargs)
        int.__setattr__(instance, 'name', name)
        int.__setattr__(instance, '_enum', enum_name)
        return instance

    def __repr__(self):
        return '<%s: %s=%d>' % (self._enum, self.name, int(self))

    def __setattr__(self, name, value):
        raise AttributeError(
            "'_EnumerationValue' object attribute '%s' is read-only" % (
            name))


class Enumeration(object):

    class __MetaEnumeration(type):

        def __new__(cls, name, bases, dct):
            # Force slots to be empty so nobody messes with the
            # enumeration and instances stay lightweight.
            dct['__slots__'] = []

            return type.__new__(cls, name, bases, dct)

        def __init__(cls, name, bases, dct):
            type.__init__(cls, name, bases, dct)

            # Create the single instance.
            cls.instance = cls.__new__(cls, first_time=True)

            # Create the enumerated attributes on the type.
            cls._values = []
            for value, member_name in enumerate(cls._enum_):
                ev = _EnumerationValue(member_name, name, value)
                setattr(cls, member_name, ev)
                cls._values.append(ev)

        def __contains__(cls, name_or_value):
            return cls.instance.__contains__(name_or_value)

    __metaclass__ = __MetaEnumeration
    __slots__ = []

    _enum_ = []

    def __new__(cls, *args, **kwargs):
        if kwargs.pop('first_time', False):
            return object.__new__(cls, *args, **kwargs)
        return cls.instance

    def __contains__(self, name_or_value):
        if type(name_or_value) == str:
            # Test for membership in our string-based list of enum
            # identifiers.
            return name_or_value in self._enum_
        else:
            # Test for membership in our list of values.
            return name_or_value in self._values

    @classmethod
    def name(cls, value):
        '''Return the name associated with value. Raises IndexError if
        value is not a member.

        If your value was obtained from the enumeration (ie is not a
        plain old int), you can also use "value.name" to get the
        name.'''
        return cls._enum_[value]


def _test():
    import doctest
    doctest.testmod()

    class ET(Enumeration):
        _enum_ = ['a', 'b', 'c']

    e = Enumeration()
    et = ET()

    assert('a' in et)
    assert('a' in ET)

    try:
        e.zzz = 6
        assert(False), "Expected AttributeError"
    except AttributeError:
        pass
    try:
        et.zzz = 6
        assert(False), "Expected AttributeError"
    except AttributeError:
        pass
    try:
        et.a = 6
        assert(False), "Expected AttributeError (r/o)"
    except AttributeError:
        pass

    # Bug: could't get enum members off the class until you
    # instantiated it once.

    class ET2(Enumeration):
        _enum_ = ['x', 'y', 'z']
    assert(ET2.x == 0)
    assert(ET2.z == 2)


if __name__ == "__main__":
    _test()
