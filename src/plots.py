"""
Visualization functions for UPL Goal Data Analysis.

This module provides reusable plotting functions for analyzing goal data.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Optional, Tuple


def set_style() -> None:
    """Set consistent matplotlib style for all plots."""
    plt.style.use("seaborn-v0_8-darkgrid")


def plot_goals_by_team(
    df: pd.DataFrame,
    column: str = "home_team",
    figsize: Tuple[int, int] = (12, 6),
    title: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """
    Plot goal count by team.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with goal data.
    column : str, optional
        Column to group by (default: 'home_team').
    figsize : tuple, optional
        Figure size (width, height). Default is (12, 6).
    title : str, optional
        Plot title. If None, uses default.
    ax : plt.Axes, optional
        Existing axes to plot on.

    Returns
    -------
    plt.Axes
        The plot axes object.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    goals_by_team = df[df["goal_minute"].notna()].groupby(column).size().sort_values(ascending=False)

    goals_by_team.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlabel("Number of Goals")
    ax.set_ylabel("Team")
    if title is None:
        title = f"Total Goals by {column.replace('_', ' ').title()}"
    ax.set_title(title)

    return ax


def plot_goals_by_season(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 6),
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """
    Plot goal count by season.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with goal data and season column.
    figsize : tuple, optional
        Figure size. Default is (12, 6).
    ax : plt.Axes, optional
        Existing axes to plot on.

    Returns
    -------
    plt.Axes
        The plot axes object.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    goals_by_season = df[df["goal_minute"].notna()].groupby("season").size()

    goals_by_season.plot(kind="bar", ax=ax, color="coral")
    ax.set_xlabel("Season")
    ax.set_ylabel("Number of Goals")
    ax.set_title("Total Goals by Season")
    ax.tick_params(axis="x", rotation=45)

    return ax


def plot_goals_by_minute(
    df: pd.DataFrame,
    bins: int = 90,
    figsize: Tuple[int, int] = (14, 6),
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """
    Plot distribution of goals by minute of match.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with goal_minute_num column.
    bins : int, optional
        Number of histogram bins. Default is 90 (one per minute).
    figsize : tuple, optional
        Figure size. Default is (14, 6).
    ax : plt.Axes, optional
        Existing axes to plot on.

    Returns
    -------
    plt.Axes
        The plot axes object.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    goals_minutes = df[df["goal_minute_num"].notna()]["goal_minute_num"]

    ax.hist(goals_minutes, bins=bins, edgecolor="black", color="green", alpha=0.7)
    ax.set_xlabel("Minute of Match")
    ax.set_ylabel("Number of Goals")
    ax.set_title("Goal Distribution by Match Minute")
    ax.axvline(45, color="red", linestyle="--", linewidth=2, label="Half Time")
    ax.legend()

    return ax


def plot_goal_type_distribution(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 6),
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """
    Plot distribution of goal types (Regular, Penalty, Own Goal).

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with goal_type column.
    figsize : tuple, optional
        Figure size. Default is (10, 6).
    ax : plt.Axes, optional
        Existing axes to plot on.

    Returns
    -------
    plt.Axes
        The plot axes object.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    goal_types = df[df["goal_minute"].notna()]["goal_type"].value_counts()

    goal_types.plot(kind="pie", ax=ax, autopct="%1.1f%%", colors=["lightblue", "orange", "red"])
    ax.set_ylabel("")
    ax.set_title("Distribution of Goal Types")

    return ax


def plot_home_vs_away(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 6),
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """
    Compare home team vs away team goals.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with team_side column.
    figsize : tuple, optional
        Figure size. Default is (10, 6).
    ax : plt.Axes, optional
        Existing axes to plot on.

    Returns
    -------
    plt.Axes
        The plot axes object.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    side_goals = df[df["goal_minute"].notna()]["team_side"].value_counts()

    side_goals.plot(kind="bar", ax=ax, color=["skyblue", "orange"])
    ax.set_xlabel("Team Side")
    ax.set_ylabel("Number of Goals")
    ax.set_title("Home Team vs Away Team Goals")
    ax.tick_params(axis="x", rotation=0)

    return ax
