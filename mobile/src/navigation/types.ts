import { Asset } from '../types';

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};

export type AppStackParamList = {
  Home: undefined;
  AddAsset: undefined;
  AssetDetail: { asset: Asset };
};
