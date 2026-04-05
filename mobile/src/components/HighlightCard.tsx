import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { Highlight } from '../types';

interface HighlightCardProps {
  highlight: Highlight;
  onPress: () => void;
}

export default function HighlightCard({ highlight, onPress }: HighlightCardProps) {
  const { colors } = useTheme();
  const isPositive = highlight.change_percent >= 0;

  return (
    <TouchableOpacity
      style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.accent }]}
      onPress={onPress}
      activeOpacity={0.85}
    >
      <View style={styles.header}>
        <View style={styles.badge}>
          <Ionicons name="star" size={12} color={colors.accent} />
          <Text style={[styles.badgeText, { color: colors.accent }]}>ATIVO EM DESTAQUE</Text>
        </View>
        <Ionicons name="chevron-forward" size={16} color={colors.textMuted} />
      </View>

      <View style={styles.body}>
        <View>
          <Text style={[styles.symbol, { color: colors.text }]}>{highlight.symbol}</Text>
          <Text style={[styles.name, { color: colors.textMuted }]}>{highlight.name}</Text>
        </View>

        <View style={styles.priceBlock}>
          <Text style={[styles.price, { color: colors.text }]}>
            R$ {highlight.price.toFixed(2)}
          </Text>
          <View
            style={[
              styles.changeBadge,
              { backgroundColor: isPositive ? colors.success + '22' : colors.danger + '22' },
            ]}
          >
            <Ionicons
              name={isPositive ? 'trending-up' : 'trending-down'}
              size={14}
              color={isPositive ? colors.success : colors.danger}
            />
            <Text
              style={[
                styles.change,
                { color: isPositive ? colors.success : colors.danger },
              ]}
            >
              {isPositive ? '+' : ''}
              {highlight.change_percent.toFixed(2)}%
            </Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1.5,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  badge: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  badgeText: { fontSize: 11, fontWeight: '700', letterSpacing: 1 },
  body: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  symbol: { fontSize: 24, fontWeight: '700' },
  name: { fontSize: 13, marginTop: 2 },
  priceBlock: { alignItems: 'flex-end', gap: 8 },
  price: { fontSize: 22, fontWeight: '700' },
  changeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
  },
  change: { fontSize: 14, fontWeight: '600' },
});
