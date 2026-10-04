import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src.data.mappings import VARIABLES
from src.data.clean_data import clean_data
from src.data.validate_data import validate_data,validate_saved_frame
from src.data.split_data import split_data

class PipelineTests(unittest.TestCase):
    def raw(self,n=100):
        df=pd.DataFrame({v:np.ones(n) for v in VARIABLES})
        df['_BMI5']=2500.
        df['_MICHD']=np.where(np.arange(n)%5==0,1.,2.)
        return df

    def test_variable_specific_codes_and_target_removal(self):
        raw=self.raw(20)
        raw.loc[0,'_AGEG5YR']=7 # A legitimate age group, never globally missing.
        raw.loc[1,'_INCOMG1']=7 # A legitimate income group.
        raw.loc[2,'DIABETE4']=2 # Pregnancy-only retained.
        raw.loc[3,'DIABETE4']=4 # Prediabetes retained.
        raw.loc[4,'GENHLTH']=7
        raw.loc[5,'_MICHD']=np.nan
        raw.loc[6,'_BMI5']=1199
        clean,_=clean_data(raw)
        validate_data(clean,raw)
        self.assertEqual(clean.loc[0,'age_group'],7)
        self.assertEqual(clean.loc[1,'income_group'],7)
        self.assertEqual(clean.loc[2,'diabetes'],2)
        self.assertEqual(clean.loc[3,'diabetes'],4)
        self.assertTrue(pd.isna(clean.loc[4,'general_health']))
        self.assertTrue(pd.isna(clean.loc[6,'bmi']))
        self.assertEqual(clean.loc[7,'bmi'],25)
        self.assertNotIn(5,clean.index)

    def test_undocumented_category_fails(self):
        raw=self.raw();raw.loc[0,'ASTHMA3']=8
        with self.assertRaises(ValueError): clean_data(raw)

    def test_saved_null_representation_and_exact_numeric_values(self):
        expected=pd.DataFrame({'bmi':pd.array([25.39,None],dtype='Float64')})
        saved=pd.DataFrame({'bmi':[25.39,np.nan]})
        validate_saved_frame(saved,expected)
        saved.loc[0,'bmi']=25.40
        with self.assertRaises(AssertionError): validate_saved_frame(saved,expected)

    def test_split_group_integrity_reproducible(self):
        raw=self.raw(1000)
        raw['GENHLTH']=1+np.arange(1000)%5
        raw['_BMI5']=2000+np.arange(1000)//2
        clean,_=clean_data(raw)
        with tempfile.TemporaryDirectory() as d:
            one=split_data(clean,Path(d));first=(Path(d)/'split_membership.csv').read_bytes()
            two=split_data(clean,Path(d))
            self.assertEqual(first,(Path(d)/'split_membership.csv').read_bytes())
            self.assertEqual(sum(map(len,one.values())),len(clean))
            for name in one: pd.testing.assert_frame_equal(one[name],two[name])

if __name__=='__main__': unittest.main()
