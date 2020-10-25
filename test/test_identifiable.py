import unittest
from classes.identifiable import Identifiable


class TestIdentifiable(unittest.TestCase):

    def test_Identifiable(self):
        identifiable = Identifiable()

        self.assertIsNone(identifiable.year())
        self.assertEqual(identifiable.ext_ids(), {})
        self.assertIsNone(identifiable.meta())

        identifiable.set_year(2000)
        self.assertEqual(identifiable.year(), 2000)

        identifiable.ext_ids()['foo'] = 'bar'
        self.assertEqual(identifiable.ext_ids()['foo'], 'bar')

        identifiable.set_meta('foo')
        self.assertEqual(identifiable.meta(), 'foo')


if __name__ == '__main__':
    unittest.main()
