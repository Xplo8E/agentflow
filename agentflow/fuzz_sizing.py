from __future__ import annotations

from typing import Any, Mapping, Protocol


class FuzzCampaignPresetLike(Protocol):
    name: str
    families: tuple[Mapping[str, str], ...]
    strategies: tuple[Mapping[str, str], ...]


def fuzz_campaign_extra_axes_cardinality(extra_axes: Mapping[str, list[Any]] | None = None) -> int:
    if extra_axes is None:
        return 1

    cardinality = 1
    for axis_name, axis_values in extra_axes.items():
        if not isinstance(axis_values, list):
            raise ValueError(f"`extra_axes.{axis_name}` must be a list")
        if not axis_values:
            raise ValueError(f"`extra_axes.{axis_name}` must contain at least one item")
        cardinality *= len(axis_values)
    return cardinality


def fuzz_campaign_preset_shard_multiple(
    *,
    preset: FuzzCampaignPresetLike,
    extra_axes: Mapping[str, list[Any]] | None = None,
) -> int:
    return len(preset.families) * len(preset.strategies) * fuzz_campaign_extra_axes_cardinality(extra_axes)


def fuzz_campaign_total_shards(
    *,
    preset: FuzzCampaignPresetLike,
    bucket_count: int,
    extra_axes: Mapping[str, list[Any]] | None = None,
) -> int:
    return fuzz_campaign_preset_shard_multiple(preset=preset, extra_axes=extra_axes) * bucket_count


def resolve_fuzz_campaign_bucket_count(
    *,
    preset: FuzzCampaignPresetLike,
    default_bucket_count: int,
    bucket_count: int | None = None,
    shards: int | None = None,
    extra_axes: Mapping[str, list[Any]] | None = None,
) -> tuple[int, int, int]:
    if bucket_count is not None and shards is not None:
        raise ValueError("use only one of `bucket_count` or `shards`")

    shard_multiple = fuzz_campaign_preset_shard_multiple(preset=preset, extra_axes=extra_axes)

    if bucket_count is not None:
        if isinstance(bucket_count, bool) or not isinstance(bucket_count, int):
            raise ValueError("`bucket_count` must be an integer")
        if bucket_count < 1:
            raise ValueError("`bucket_count` must be at least 1")
        resolved_bucket_count = bucket_count
    elif shards is not None:
        if isinstance(shards, bool) or not isinstance(shards, int):
            raise ValueError("`shards` must be an integer")
        if shards < 1:
            raise ValueError("`shards` must be at least 1")
        if shards % shard_multiple != 0:
            raise ValueError(
                f"`shards` must be a multiple of {shard_multiple} for preset `{preset.name}`, got `{shards}`"
            )
        resolved_bucket_count = shards // shard_multiple
    else:
        resolved_bucket_count = default_bucket_count

    total_shards = shard_multiple * resolved_bucket_count
    return resolved_bucket_count, total_shards, shard_multiple


__all__ = [
    "FuzzCampaignPresetLike",
    "fuzz_campaign_extra_axes_cardinality",
    "fuzz_campaign_preset_shard_multiple",
    "fuzz_campaign_total_shards",
    "resolve_fuzz_campaign_bucket_count",
]
