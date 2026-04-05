import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { Asset } from '../types';

interface AssetCardProps {
  asset: Asset;
  isHighlight?: boolean;
  onPress: () => void;
  onDelete: () => void;
}

export default function AssetCard({ asset, isHighlight, onPress, onDelete }: AssetCardProps) {
  const { colors } = useTheme();

  return (
    <TouchableOpacity
      style={[
        styles.card,
        {
          backgroundColor: colors.surface,
          borderColor: isHighlight ? colors.accent : colors.border,
          borderWidth: isHighlight ? 1.5 : 1,
        },
      ]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <View style={[styles.symbolBadge, { backgroundColor: isHighlight ? colors.accent + '22' : colors.surfaceHigh }]}>
        <Text style={[styles.symbolText, { color: isHighlight ? colors.accent : colors.text }]}>
          {asset.symbol}
        </Text>
      </View>

      <View style={styles.info}>
        <Text style={[styles.name, { color: colors.text }]} numberOfLines={1}>
          {asset.name}
        </Text>
        <Text style={[styles.date, { color: colors.textMuted }]}>
          {isHighlight && (
            <Text style={{ color: colors.accent }}>★ Destaque  </Text>
          )}
          {new Date(asset.created_at).toLocaleDateString('pt-BR')}
        </Text>
      </View>

      <View style={styles.actions}>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
        <TouchableOpacity onPress={onDelete} style={styles.deleteBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
          <Ionicons name="trash-outline" size={18} color={colors.danger} />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 14,
    padding: 16,
    marginBottom: 10,
    gap: 12,
  },
  symbolBadge: {
    width: 52,
    height: 52,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  symbolText: { fontSize: 13, fontWeight: '700', letterSpacing: 0.5 },
  info: { flex: 1 },
  name: { fontSize: 15, fontWeight: '600', marginBottom: 4 },
  date: { fontSize: 12 },
  actions: { alignItems: 'center', gap: 8 },
  deleteBtn: { marginTop: 4 },
});
