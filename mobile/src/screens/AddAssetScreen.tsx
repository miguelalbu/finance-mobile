import { Ionicons } from '@expo/vector-icons';
import { useQueryClient } from '@tanstack/react-query';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Button from '../components/Button';
import Input from '../components/Input';
import { useTheme } from '../context/ThemeContext';
import { AppStackParamList } from '../navigation/types';
import { assetsApi } from '../services/api';

const SUGGESTIONS = [
  { symbol: 'PETR4', name: 'Petrobras PN' },
  { symbol: 'VALE3', name: 'Vale ON' },
  { symbol: 'ITUB4', name: 'Itaú Unibanco PN' },
  { symbol: 'BBDC4', name: 'Bradesco PN' },
  { symbol: 'ABEV3', name: 'Ambev ON' },
];

type Props = { navigation: NativeStackNavigationProp<AppStackParamList, 'AddAsset'> };

export default function AddAssetScreen({ navigation }: Props) {
  const { colors } = useTheme();
  const queryClient = useQueryClient();

  const [symbol, setSymbol] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fillSuggestion = (s: { symbol: string; name: string }) => {
    setSymbol(s.symbol);
    setName(s.name);
    setError('');
  };

  const handleSave = async () => {
    if (!symbol.trim() || !name.trim()) {
      setError('Preencha o símbolo e o nome do ativo');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await assetsApi.create(symbol.trim().toUpperCase(), name.trim());
      queryClient.invalidateQueries({ queryKey: ['assets'] });
      navigation.goBack();
    } catch {
      setError('Não foi possível adicionar o ativo. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]} edges={['bottom']}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <Text style={[styles.subtitle, { color: colors.textMuted }]}>
            Informe o código e o nome do ativo que deseja acompanhar.
          </Text>

          {error ? (
            <View style={[styles.errorBox, { backgroundColor: colors.danger + '18', borderColor: colors.danger + '44' }]}>
              <Ionicons name="alert-circle-outline" size={16} color={colors.danger} />
              <Text style={[styles.errorText, { color: colors.danger }]}>{error}</Text>
            </View>
          ) : null}

          <Input
            label="Símbolo"
            value={symbol}
            onChangeText={(t) => setSymbol(t.toUpperCase())}
            placeholder="Ex: PETR4"
            autoCapitalize="characters"
          />
          <Input
            label="Nome"
            value={name}
            onChangeText={setName}
            placeholder="Ex: Petrobras PN"
          />

          {/* Sugestões */}
          <Text style={[styles.suggestLabel, { color: colors.textMuted }]}>Sugestões</Text>
          <View style={styles.suggestions}>
            {SUGGESTIONS.map((s) => (
              <Button
                key={s.symbol}
                label={s.symbol}
                variant="outline"
                onPress={() => fillSuggestion(s)}
                style={styles.chip}
              />
            ))}
          </View>

          <View style={[styles.infoBox, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <Ionicons name="information-circle-outline" size={16} color={colors.textMuted} />
            <Text style={[styles.infoText, { color: colors.textMuted }]}>
              Use o código do ativo na bolsa (ex: PETR4, VALE3). A cotação será buscada automaticamente.
            </Text>
          </View>
        </ScrollView>

        <View style={[styles.footer, { backgroundColor: colors.background, borderTopColor: colors.border }]}>
          <Button label="Adicionar ativo" onPress={handleSave} loading={loading} />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  flex: { flex: 1 },
  scroll: { padding: 20, paddingBottom: 0 },
  subtitle: { fontSize: 14, lineHeight: 20, marginBottom: 24 },
  errorBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    marginBottom: 12,
  },
  errorText: { fontSize: 13, flex: 1 },
  suggestLabel: { fontSize: 12, fontWeight: '600', letterSpacing: 0.5, marginBottom: 10, marginTop: 4 },
  suggestions: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 20 },
  chip: { height: 36, paddingHorizontal: 14 },
  infoBox: {
    flexDirection: 'row',
    gap: 8,
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'flex-start',
  },
  infoText: { flex: 1, fontSize: 13, lineHeight: 18 },
  footer: { padding: 20, paddingBottom: 32, borderTopWidth: 1 },
});
