import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import React from 'react';
import { Dimensions, ScrollView, StyleSheet, Text, View } from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { SafeAreaView } from 'react-native-safe-area-context';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import { useTheme } from '../context/ThemeContext';
import { AppStackParamList } from '../navigation/types';
import { quotesApi } from '../services/api';

const { width } = Dimensions.get('window');

type Props = {
  navigation: NativeStackNavigationProp<AppStackParamList, 'AssetDetail'>;
  route: RouteProp<AppStackParamList, 'AssetDetail'>;
};

export default function AssetDetailScreen({ route }: Props) {
  const { asset } = route.params;
  const { colors, isDark } = useTheme();

  const { data: quote, isLoading: loadingQuote } = useQuery({
    queryKey: ['quote', asset.symbol],
    queryFn: () => quotesApi.getQuote(asset.symbol).then((r) => r.data),
    retry: false,
  });

  const { data: history, isLoading: loadingHistory } = useQuery({
    queryKey: ['history', asset.symbol],
    queryFn: () => quotesApi.getHistory(asset.symbol).then((r) => r.data),
    retry: false,
  });

  const isPositive = (quote?.regularMarketChangePercent ?? 0) >= 0;
  const changeColor = isPositive ? colors.success : colors.danger;

  const chartData = history && history.length > 0
    ? history.slice(-30).map((h) => h.price)
    : [];

  const chartLabels = history && history.length > 0
    ? history.slice(-30).map((h, i) => {
        if (i === 0 || i === Math.floor(history.length / 2) || i === history.length - 1) {
          return new Date(h.fetched_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
        }
        return '';
      })
    : [];

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.background }]} edges={['bottom']}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>

        {/* Cabeçalho do ativo */}
        <View style={[styles.assetHeader, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={[styles.symbolBadge, { backgroundColor: colors.accent + '22' }]}>
            <Text style={[styles.symbolText, { color: colors.accent }]}>{asset.symbol}</Text>
          </View>
          <View style={styles.assetInfo}>
            <Text style={[styles.assetName, { color: colors.text }]}>{asset.name}</Text>
            <Text style={[styles.assetSince, { color: colors.textMuted }]}>
              Desde {new Date(asset.created_at).toLocaleDateString('pt-BR')}
            </Text>
          </View>
        </View>

        {/* Cotação */}
        <Text style={[styles.sectionTitle, { color: colors.textMuted }]}>COTAÇÃO ATUAL</Text>
        {loadingQuote ? (
          <View style={styles.loadingBox}><LoadingSpinner /></View>
        ) : quote ? (
          <View style={[styles.quoteCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <View style={styles.priceRow}>
              <Text style={[styles.price, { color: colors.text }]}>
                R$ {quote.regularMarketPrice?.toFixed(2) ?? '—'}
              </Text>
              <View style={[styles.changeBadge, { backgroundColor: changeColor + '22' }]}>
                <Ionicons
                  name={isPositive ? 'trending-up' : 'trending-down'}
                  size={16}
                  color={changeColor}
                />
                <Text style={[styles.changeText, { color: changeColor }]}>
                  {isPositive ? '+' : ''}{quote.regularMarketChangePercent?.toFixed(2) ?? '0'}%
                </Text>
              </View>
            </View>

            <View style={[styles.divider, { backgroundColor: colors.border }]} />

            <View style={styles.statsRow}>
              <View style={styles.stat}>
                <Text style={[styles.statLabel, { color: colors.textMuted }]}>Fechamento ant.</Text>
                <Text style={[styles.statValue, { color: colors.text }]}>
                  R$ {quote.regularMarketPreviousClose?.toFixed(2) ?? '—'}
                </Text>
              </View>
              <View style={styles.stat}>
                <Text style={[styles.statLabel, { color: colors.textMuted }]}>Volume</Text>
                <Text style={[styles.statValue, { color: colors.text }]}>
                  {quote.regularMarketVolume
                    ? (quote.regularMarketVolume / 1_000_000).toFixed(2) + 'M'
                    : '—'}
                </Text>
              </View>
              <View style={styles.stat}>
                <Text style={[styles.statLabel, { color: colors.textMuted }]}>Nome</Text>
                <Text style={[styles.statValue, { color: colors.text }]} numberOfLines={1}>
                  {quote.shortName ?? asset.name}
                </Text>
              </View>
            </View>
          </View>
        ) : (
          <View style={[styles.emptyCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <Ionicons name="cloud-offline-outline" size={24} color={colors.textMuted} />
            <Text style={[styles.emptyCardText, { color: colors.textMuted }]}>
              Cotação indisponível no momento
            </Text>
          </View>
        )}

        {/* Gráfico */}
        <Text style={[styles.sectionTitle, { color: colors.textMuted, marginTop: 24 }]}>
          HISTÓRICO DE PREÇOS
        </Text>

        {loadingHistory ? (
          <View style={styles.loadingBox}><LoadingSpinner /></View>
        ) : chartData.length > 1 ? (
          <View style={[styles.chartCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <LineChart
              data={{
                labels: chartLabels,
                datasets: [{ data: chartData, strokeWidth: 2 }],
              }}
              width={width - 48}
              height={200}
              chartConfig={{
                backgroundGradientFrom: colors.surface,
                backgroundGradientTo: colors.surface,
                decimalPlaces: 2,
                color: (opacity = 1) =>
                  isDark
                    ? `rgba(56, 189, 248, ${opacity})`
                    : `rgba(2, 132, 199, ${opacity})`,
                labelColor: () => colors.textMuted,
                style: { borderRadius: 12 },
                propsForDots: { r: '3', strokeWidth: '1', stroke: colors.accent },
                propsForBackgroundLines: { stroke: colors.border, strokeDasharray: '' },
              }}
              bezier
              style={styles.chart}
              withInnerLines
              withOuterLines={false}
            />
            <Text style={[styles.chartFooter, { color: colors.textMuted }]}>
              Últimos {chartData.length} registros
            </Text>
          </View>
        ) : (
          <View style={[styles.emptyCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <EmptyState
              icon="analytics-outline"
              title="Histórico indisponível"
              subtitle="Os dados históricos aparecerão após a primeira atualização automática"
            />
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  scroll: { padding: 20, paddingBottom: 40 },
  assetHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
    marginBottom: 24,
  },
  symbolBadge: { width: 56, height: 56, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  symbolText: { fontSize: 14, fontWeight: '700', letterSpacing: 0.5 },
  assetInfo: { flex: 1 },
  assetName: { fontSize: 17, fontWeight: '600' },
  assetSince: { fontSize: 12, marginTop: 3 },
  sectionTitle: { fontSize: 11, fontWeight: '700', letterSpacing: 1, marginBottom: 10 },
  loadingBox: { height: 120, justifyContent: 'center' },
  quoteCard: { borderRadius: 14, padding: 20, borderWidth: 1, marginBottom: 4 },
  priceRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  price: { fontSize: 32, fontWeight: '700' },
  changeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  changeText: { fontSize: 15, fontWeight: '600' },
  divider: { height: 1, marginVertical: 16 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between' },
  stat: { flex: 1 },
  statLabel: { fontSize: 11, fontWeight: '500', marginBottom: 4 },
  statValue: { fontSize: 13, fontWeight: '600' },
  emptyCard: { borderRadius: 14, borderWidth: 1, padding: 20, alignItems: 'center', gap: 8 },
  emptyCardText: { fontSize: 13 },
  chartCard: { borderRadius: 14, borderWidth: 1, padding: 16, alignItems: 'center' },
  chart: { borderRadius: 12 },
  chartFooter: { fontSize: 11, marginTop: 8 },
});
