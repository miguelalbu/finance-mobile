import { Ionicons } from '@expo/vector-icons';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useFocusEffect } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback } from 'react';
import {
  Alert,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AssetCard from '../components/AssetCard';
import EmptyState from '../components/EmptyState';
import HighlightCard from '../components/HighlightCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { useTheme } from '../context/ThemeContext';
import { AppStackParamList } from '../navigation/types';
import { assetsApi, quotesApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { Asset } from '../types';

type Props = { navigation: NativeStackNavigationProp<AppStackParamList, 'Home'> };

export default function HomeScreen({ navigation }: Props) {
  const { colors, isDark, toggleTheme } = useTheme();
  const clearToken = useAuthStore((s) => s.clearToken);
  const queryClient = useQueryClient();

  const {
    data: assets,
    isLoading,
    isRefetching,
    refetch,
  } = useQuery({ queryKey: ['assets'], queryFn: () => assetsApi.list().then((r) => r.data) });

  const { data: highlight } = useQuery({
    queryKey: ['highlight'],
    queryFn: () => quotesApi.getHighlight().then((r) => r.data),
    retry: false,
  });

  // Sempre que o HomeScreen ganhar foco (ex: voltar do AssetDetail),
  // revalida o highlight para refletir novos históricos gerados
  useFocusEffect(
    useCallback(() => {
      queryClient.invalidateQueries({ queryKey: ['highlight'] });
    }, [queryClient])
  );

  const handleDelete = (asset: Asset) => {
    Alert.alert('Remover ativo', `Deseja remover ${asset.symbol} dos seus favoritos?`, [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Remover',
        style: 'destructive',
        onPress: async () => {
          await assetsApi.remove(asset.id);
          queryClient.invalidateQueries({ queryKey: ['assets'] });
          queryClient.invalidateQueries({ queryKey: ['highlight'] });
        },
      },
    ]);
  };

  const handleLogout = () => {
    Alert.alert('Sair', 'Deseja encerrar a sessão?', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Sair', style: 'destructive', onPress: clearToken },
    ]);
  };

  if (isLoading) return <LoadingSpinner message="Carregando ativos..." />;

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <View>
          <Text style={[styles.greeting, { color: colors.textMuted }]}>Bem-vindo</Text>
          <Text style={[styles.title, { color: colors.text }]}>Meus Ativos</Text>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity
            onPress={toggleTheme}
            style={[styles.iconBtn, { backgroundColor: colors.surface }]}
          >
            <Ionicons
              name={isDark ? 'sunny-outline' : 'moon-outline'}
              size={20}
              color={colors.textMuted}
            />
          </TouchableOpacity>
          <TouchableOpacity
            onPress={handleLogout}
            style={[styles.iconBtn, { backgroundColor: colors.surface }]}
          >
            <Ionicons name="log-out-outline" size={20} color={colors.danger} />
          </TouchableOpacity>
        </View>
      </View>

      <FlatList
        data={assets}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={() => {
              refetch();
              queryClient.invalidateQueries({ queryKey: ['highlight'] });
            }}
            tintColor={colors.accent}
          />
        }
        ListHeaderComponent={
          <>
            {highlight && (
              <HighlightCard
                highlight={highlight}
                onPress={() => {
                  const asset = assets?.find((a) => a.id === highlight.asset_id);
                  if (asset) navigation.navigate('AssetDetail', { asset });
                }}
              />
            )}
            <View style={styles.sectionHeader}>
              <Text style={[styles.sectionTitle, { color: colors.text }]}>Favoritos</Text>
              <Text style={[styles.sectionCount, { color: colors.textMuted }]}>
                {assets?.length ?? 0} ativo{(assets?.length ?? 0) !== 1 ? 's' : ''}
              </Text>
            </View>
          </>
        }
        ListEmptyComponent={
          <EmptyState
            icon="star-outline"
            title="Nenhum ativo cadastrado"
            subtitle="Toque no botão + para adicionar seu primeiro ativo favorito"
          />
        }
        renderItem={({ item }) => (
          <AssetCard
            asset={item}
            isHighlight={!!highlight && Number(item.id) === Number(highlight.asset_id)}
            onPress={() => navigation.navigate('AssetDetail', { asset: item })}
            onDelete={() => handleDelete(item)}
          />
        )}
      />

      {/* FAB */}
      <TouchableOpacity
        style={[styles.fab, { backgroundColor: colors.accent }]}
        onPress={() => navigation.navigate('AddAsset')}
        activeOpacity={0.85}
      >
        <Ionicons name="add" size={28} color={colors.white} />
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
  },
  greeting: { fontSize: 12, fontWeight: '500' },
  title: { fontSize: 24, fontWeight: '700' },
  headerActions: { flexDirection: 'row', gap: 8 },
  iconBtn: { padding: 10, borderRadius: 10 },
  list: { padding: 20, paddingBottom: 100 },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: { fontSize: 16, fontWeight: '600' },
  sectionCount: { fontSize: 13 },
  fab: {
    position: 'absolute',
    bottom: 32,
    right: 24,
    width: 58,
    height: 58,
    borderRadius: 29,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
});
